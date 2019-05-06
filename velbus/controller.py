"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import time
import velbus
from velbus.parser import VelbusParser
from velbus.connections.socket import SocketConnection
from velbus.connections.serial import USBConnection


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
            self.connection = USBConnection(port, self)

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

            def module_loaded():
                self._nb_of_modules_loaded += 1
                if self._nb_of_modules_loaded >= len(self._modules):
                    callback()
            for module in self._modules:
                self._modules[module].load(module_loaded)
        for address in range(0, 256):
            message = velbus.ModuleTypeRequestMessage(address)
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
        if isinstance(message, velbus.Message):
            self.send(message, callback)

    def new_message(self, message):
        """
        :return: None
        """
        self.logger.info("New message: " + str(message))
        if isinstance(message, velbus.BusActiveMessage):
            self.logger.info("Velbus active message received")
        if isinstance(message, velbus.ReceiveReadyMessage):
            self.logger.info("Velbus receive ready message received")
        if isinstance(message, velbus.BusOffMessage):
            self.logger.error("Velbus bus off message received")
        if isinstance(message, velbus.ReceiveBufferFullMessage):
            self.logger.error("Velbus receive buffer full message received")
        if isinstance(message, velbus.ModuleTypeMessage):
            self.logger.debug("Module type response received")
            name = message.module_name()
            address = message.address
            m_type = message.module_type
            if name == "Unknown":
                self.logger.warning("Unknown module (code: " + str(message.module_type) + ')')
                return
            if name in velbus.ModuleRegistry:
                module = velbus.ModuleRegistry[name](m_type, name, address, self)
                self._modules[address] = module
            else:
                self.logger.warning("Module " + name + " is not yet supported.")
        for subscriber in self.__subscribers:
            subscriber(message)

    def stop(self):
        """
        Stop velbus
        """
        self.connection.stop()

    def sync_clock(self):
        """
        This will send all the needed messages to sync the cloc
        """
        self.send(velbus.SetRealtimeClock())
        self.send(velbus.SetDate())
        self.send(velbus.SetDaylightSaving())
