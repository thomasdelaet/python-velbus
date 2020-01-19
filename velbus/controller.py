"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import time
import threading
from velbus.parser import VelbusParser
from velbus.connections.socket import SocketConnection
from velbus.connections.serial import VelbusUSBConnection
from velbus.messages.module_type_request import ModuleTypeRequestMessage
from velbus.message import Message
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
        self.logger = logging.getLogger('velbus')
        self.parser = VelbusParser(self)
        self.__subscribers = []
        self.__scan_callback = None
        self._modules = {}
        if ":" in port:
            self.connection = SocketConnection(port, self)
        else:
            self.connection = VelbusUSBConnection(port, self)

    def feed_parser(self, data):
        """
        Feed parser with new data

        :return: None
        """
        assert isinstance(data, bytes)
        self.parser.feed(data)

    def subscribe(self, subscriber):
        """
        :return: None
        """
        self.__subscribers.append(subscriber)

    def parse(self, binary_message):
        """
        :return: velbus.Message or None
        """
        return self.parser.parse(binary_message)

    def unsubscribe(self, subscriber):
        """
        :return: None
        """
        self.__subscribers.remove(subscriber)

    def send(self, message, callback=None):
        """
        :return: None
        """
        self.connection.send(message, callback)

    def get_modules(self):
        """
        Returns a list of modules from a specific category

        :return: list
        """
        return self._modules.values()

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
            logging.info('Scan finished')
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

            def timeout_expired():
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

            # 60 second timeout for loading modules
            self.load_timeout = threading.Timer(60, timeout_expired).start()
            for module in self._modules:
                self._modules[module].load(module_loaded)

        for address in range(0, 256):
            message = ModuleTypeRequestMessage(address)
            if address == 255:
                self.send(message, scan_finished)
            else:
                self.send(message)

    def send_binary(self, binary_message, callback=None):
        """
        :return: None
        """
        assert isinstance(binary_message, str)
        message = self.parser.parse(binary_message)
        if isinstance(message, Message):
            self.send(message, callback)

    def new_message(self, message):
        """
        :return: None
        """
        self.logger.info("New message: " + str(message))
        if isinstance(message, BusActiveMessage):
            self.logger.info("Velbus active message received")
        if isinstance(message, ReceiveReadyMessage):
            self.logger.info("Velbus receive ready message received")
        if isinstance(message, BusOffMessage):
            self.logger.error("Velbus bus off message received")
        if isinstance(message, ReceiveBufferFullMessage):
            self.logger.error("Velbus receive buffer full message received")
        if isinstance(message, ModuleTypeMessage):
            self.logger.debug(
                "Module type response received from address "
                + str(message.address)
            )
            name = message.module_name()
            address = message.address
            m_type = message.module_type
            if name == "Unknown":
                self.logger.warning(
                    "Unknown module (code: " + str(message.module_type) + ')'
                )
                return
            if name in ModuleRegistry:
                module = ModuleRegistry[name](m_type, name, address, self)
                self._modules[address] = module
            else:
                self.logger.warning("Module " + name + " is not yet supported")
        if isinstance(message, ModuleSubTypeMessage):
            self.logger.debug(
                "Module subtype response received from address "
                + str(message.address)
            )
            name = message.module_name()
            address = message.address
            m_type = message.module_type
            if name == "Unknown":
                self.logger.warning(
                    "Unknown module (code: " + str(message.module_type) + ')'
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
                    self._modules[message.sub_address_1] = module
                if message.sub_address_2 != 0xFF:
                    module = ModuleRegistry[subname](
                        m_type,
                        subname,
                        message.sub_address_2,
                        address,
                        2,
                        self,
                    )
                    self._modules[message.sub_address_2] = module
                if message.sub_address_3 != 0xFF:
                    module = ModuleRegistry[subname](
                        m_type,
                        subname,
                        message.sub_address_3,
                        address,
                        3,
                        self,
                    )
                    self._modules[message.sub_address_3] = module
                if (
                    message.sub_address_4 != 0xFF
                    and name != "VMBGPOD"
                    and name != "VMBGPO"
                ):
                    module = ModuleRegistry[subname](
                        m_type,
                        subname,
                        message.sub_address_4,
                        address,
                        4,
                        self,
                    )
                    self._modules[message.sub_address_4] = module
            else:
                self.logger.warning(
                    "Module " + name + " does not yet support sub modules"
                )
        for subscriber in self.__subscribers:
            subscriber(message)

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
