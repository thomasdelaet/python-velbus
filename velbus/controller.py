"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import time
import threading
import pkg_resources
import json
import functools
from velbus.parser import VelbusParser
from velbus.connections.socket import SocketConnection
from velbus.connections.serial import VelbusUSBConnection
from velbus.message import Message
from velbus.messages.module_type_request import ModuleTypeRequestMessage
from velbus.messages.bus_active import BusActiveMessage
from velbus.messages.receive_ready import ReceiveReadyMessage
from velbus.messages.bus_off import BusOffMessage
from velbus.module_registry import ModuleRegistry
from velbus.messages.receive_buffer_full import ReceiveBufferFullMessage
from velbus.messages.module_type import ModuleTypeMessage
from velbus.messages.module_subtype import ModuleSubTypeMessage
from velbus.messages.set_realtime_clock import SetRealtimeClock
from velbus.messages.set_daylight_saving import SetDaylightSaving
from velbus.messages.set_date import SetDate


class Controller(object):
    """
    Velbus Bus connection controller
    """

    def __init__(self, port):
        self.logger = logging.getLogger("velbus")
        self.parser = VelbusParser(self)
        self.__message_subscribers = []
        self.__module_subscribers = {}
        self.__scan_callback = None
        self._modules = {}
        self._loadModuleData()
        if ":" in port:
            if port.startswith("tls://"):
                self.connection = SocketConnection(
                    port.replace("tls://", ""), self, True
                )
            else:
                self.connection = SocketConnection(port, self, False)
        else:
            self.connection = VelbusUSBConnection(port, self)

    def _loadModuleData(self):
        filepath = pkg_resources.resource_filename(__name__, "data.json")
        with open(filepath) as json_file:
            self._module_data = json.load(json_file)

    # interface towards connection objects

    def feed_parser(self, data):
        """
        Feed parser with new data

        :return: None
        """
        assert isinstance(data, bytes)
        self.parser.feed(data)

    # event interface

    def subscribe(self, subscriber):
        """
        :return: None
        """
        self.__message_subscribers.append(subscriber)

    def subscribe_module(self, subscriber, category):
        """
        :return: None
        """
        if category not in self.__module_subscribers:
            self.__module_subscribers[category] = []
        self.__module_subscribers[category].append(subscriber)

    def unsubscribe(self, subscriber):
        """
        :return: None
        """
        self.__message_subscribers.remove(subscriber)

    def unsubscribe_module(self, subscriber, category):
        """
        :return: None
        """
        self.__module_subscribers[category].remove(subscriber)

    # command interface

    def send(self, message, callback=None):
        """
        :return: None
        """
        self.connection.send(message, callback)

    def get_modules(self):
        """
        Returns a list of modules

        :return: list
        """
        return self._modules.values()

    def get_modules_loaded(self):
        """
        Returns a list of loaded modules

        :return: list
        """
        result = []
        for module in self.get_modules():
            if module.loaded:
                result.append(module)
        return result

    def get_module(self, address):
        """
        Returns module at address
        """
        return self._modules[address]

    def scan(self, callback=None):
        """
        Scan the bus and call the callback when a new module is discovered

        :return: None
        """

        def scan_finished():
            """
            Callback when scan is finished
            """
            time.sleep(3)
            logging.info("Scan finished")
            self._nb_of_modules_loaded = 0
            self._load_finished = False

            def module_loaded():
                self._nb_of_modules_loaded += 1
                self.logger.debug(
                    "Loaded modules "
                    + str(self._nb_of_modules_loaded)
                    + " of "
                    + str(len(self._modules))
                )
                if self._nb_of_modules_loaded >= len(self._modules):
                    self._load_finished = True
                    callback()

            def final_timeout_expired():
                if not self._load_finished:
                    modules_not_loaded = []
                    for module in self._modules:
                        if not self._modules[module].loaded:
                            self.logger.warning(
                                "Failed to completely load module "
                                + str(self._modules[module].get_module_name())
                                + " at address "
                                + str(self._modules[module].get_module_address())
                                + " before timeout expired."
                            )
                            modules_not_loaded.append(module)
                    for module in modules_not_loaded:
                        del self._modules[module]
                    callback()

            def first_retry():
                if not self._load_finished:
                    # First load failed, do 2nd retry for failed modules
                    _missing_modules = 0
                    for module in self._modules:
                        if not self._modules[module].loaded:
                            self.logger.warning(
                                "Failed to load module "
                                + str(self._modules[module].get_module_name())
                                + " at address "
                                + str(self._modules[module].get_module_address())
                                + ", retry initiated."
                            )
                            # Trigger load without callback
                            self._modules[module].load(None)
                            _missing_modules += 1
                    # Set final timeout
                    threading.Timer(
                        (_missing_modules * 10) + 1, final_timeout_expired
                    ).start()

            # Set first timeout to 10 second for each module to trigger a retry
            threading.Timer((len(self._modules) * 10) + 1, first_retry).start()

            for module in self._modules:
                self._modules[module].load(module_loaded)
                time.sleep(1)  # Throttle loading modules

        for address in range(0, 256):
            message = ModuleTypeRequestMessage(address)
            if address == 255:
                self.send(message, scan_finished)
            else:
                self.send(message)

    def async_scan(self):
        for address in range(0, 256):
            message = ModuleTypeRequestMessage(address)
            self.send(message)

    def stop(self):
        """
        Stop velbus
        """
        self.connection.stop()

    def sync_clock(self):
        """
        This will send all the needed messages to sync the clock
        """
        self.send(SetRealtimeClock())
        self.send(SetDate())
        self.send(SetDaylightSaving())

    # messaging and module loading logic

    def new_message(self, message):
        """
        :return: None
        """
        self.logger.info("New message: " + str(message))
        if isinstance(message, ModuleTypeMessage):
            self._process_module_type_message(message)
        elif isinstance(message, ModuleSubTypeMessage):
            self._process_module_subtype_message(message)
        elif isinstance(message, BusActiveMessage):
            self.logger.info("Velbus active message received")
        elif isinstance(message, ReceiveReadyMessage):
            self.logger.info("Velbus receive ready message received")
        elif isinstance(message, BusOffMessage):
            self.logger.error("Velbus bus off message received")
        elif isinstance(message, ReceiveBufferFullMessage):
            self.logger.error("Velbus receive buffer full message received")
        # notify everyone who requests it
        for subscriber in self.__message_subscribers:
            subscriber(message)

    def _process_module_type_message(self, message):
        """
        Process ModuleType message and if new module: add to module repository
        """
        self.logger.debug(
            "Module type response received from address " + str(message.address)
        )
        name = message.module_name()
        address = message.address
        m_type = message.module_type
        if name == "Unknown":
            self.logger.warning(
                "Unknown module (code: " + str(message.module_type) + ")"
            )
            return
        if name in ModuleRegistry:
            module = ModuleRegistry[name](m_type, name, address, self)
            self._add_module(address, module)
        elif name in ["VMBSIG", "VMBUSBIP"]:
            self.logger.info("Module " + name + " is a config module, ignoring")
        else:
            self.logger.warning("Module " + name + " is not yet supported")

    def _process_module_subtype_message(self, message):
        """
        Process ModuleSubType message and if new module: add to module repository
        """
        self.logger.debug(
            "Module subtype response received from address " + str(message.address)
        )
        name = message.module_name()
        address = message.address
        m_type = message.module_type
        if name == "Unknown":
            self.logger.warning(
                "Unknown module (code: " + str(message.module_type) + ")"
            )
            return
        if "SUB_" + name in ModuleRegistry:
            subname = "SUB_" + name
            if message.sub_address_1 != 0xFF:
                module = ModuleRegistry[subname](
                    m_type,
                    subname,
                    message.sub_address_1,
                    address,
                    1,
                    self,
                )
                self._add_module(message.sub_address_1, module)
            if message.sub_address_2 != 0xFF:
                module = ModuleRegistry[subname](
                    m_type,
                    subname,
                    message.sub_address_2,
                    address,
                    2,
                    self,
                )
                self._add_module(message.sub_address_2, module)
            if message.sub_address_3 != 0xFF:
                module = ModuleRegistry[subname](
                    m_type,
                    subname,
                    message.sub_address_3,
                    address,
                    3,
                    self,
                )
                self._add_module(message.sub_address_3, module)
            if (
                message.sub_address_4 != 0xFF
                and name != "VMBGPOD"
                and name != "VMBGPO"
                and name != "VMBELO"
            ):
                module = ModuleRegistry[subname](
                    m_type,
                    subname,
                    message.sub_address_4,
                    address,
                    4,
                    self,
                )
                self._add_module(message.sub_address_4, module)
        else:
            self.logger.warning("Module " + name + " does not yet support sub modules")

    def _add_module(self, address, module):
        callback = functools.partial(self._module_loaded, module)
        if address not in self._modules:
            self.logger.info("adding module at address %s", address)
            self._modules[address] = module
            module.load(callback)
        else:
            if self._modules[address].loaded:
                self.logger.info(
                    "module already in registry at address %s and loaded", address
                )
            else:
                self.logger.info("loading module at address %s", address)
                module.load(callback)

    def _module_loaded(self, module):
        for channel in range(1, module.number_of_channels() + 1):
            categories = module.get_categories(channel)
            for category in categories:
                if category in self.__module_subscribers:
                    for subscriber in self.__module_subscribers[category]:
                        subscriber(module, channel)

    # probably not used

    def parse(self, binary_message):
        """
        :return: velbus.Message or None
        """
        return self.parser.parse(binary_message)

    def send_binary(self, binary_message, callback=None):
        """
        :return: None
        """
        assert isinstance(binary_message, str)
        message = self.parser.parse(binary_message)
        if isinstance(message, Message):
            self.send(message, callback)

    def new_binary_message(self, message):
        assert isinstance(message, bytes)
        message = self.parser.parse_binary_message(message)
        if isinstance(message, Message):
            self.new_message(message)
