"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import velbus


class VelbusConnection(object):
    """
    Generic Velbus connection
    """

    controller = None

    def set_controller(self, controller):
        """
        @return: None
        """
        assert isinstance(controller, Controller)
        self.controller = controller

    def send(self, message):
        """
        @return: None
        """
        raise NotImplementedError


class Controller(object):
    """
    Velbus Bus connection controller
    """

    def __init__(self, connection):
        self.logger = logging.getLogger('velbus')
        self.connection = connection
        self.parser = velbus.VelbusParser(self)
        self.__subscribers = []
        self.connection.set_controller(self)
        self.__scan_callback = None

    def feed_parser(self, data):
        """
        Feed parser with new data

        @return: None
        """
        assert isinstance(data, bytes)
        self.parser.feed(data)

    def subscribe(self, subscriber):
        """
        @return: None
        """
        self.__subscribers.append(subscriber)

    def parse(self, binary_message):
        """
        @return: velbus.Message or None
        """
        return self.parser.parse(binary_message)

    def unsubscribe(self, subscriber):
        """
        @return: None
        """
        self.__subscribers.remove(subscriber)

    def send(self, message):
        """
        @return: None
        """
        self.connection.send(message)

    def scan(self, callback):
        """
        Scan the bus and return callback with all available modules

        @return: None
        """
        if self.__scan_callback:
            raise Exception("Scan already in progress, wait till finished")
        self.__scan_callback = callback
        for address in range(1, 255):
            message = velbus.ModuleTypeRequestMessage(address)
            self.send(message)
        #FIXME: Wait a number of seconds before returning

    def send_binary(self, binary_message):
        """
        @return: None
        """
        assert isinstance(binary_message, str)
        message = self.parser.parse(binary_message)
        if isinstance(message, velbus.Message):
            self.send(message)

    def new_message(self, message):
        """
        @return: None
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
            self.logger.error("Module type response received")
        for subscriber in self.__subscribers:
            subscriber(message)
