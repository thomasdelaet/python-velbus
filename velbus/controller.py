"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import logging


class VelbusConnection(object):
    # pylint: disable-msg=R0921
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

    def feed_parser(self, data):
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
        for subscriber in self.__subscribers:
            subscriber(message)
