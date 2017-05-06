"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import time
import velbus
import binascii
import serial
import serial_asyncio
import logging
import asyncio

class Output(asyncio.Protocol):
    """Protocol class."""

    def __init__(self):
        super().__init__()

    def set_connection(self, connection):
        self._connection = connection
        self._connection.set_protocol(self)

    def connection_made(self, transport):
        """Initiate."""
        self._transport = transport

    def data_received(self, data):
        """On read."""
        self._connection.feed_parser(data)

    def connection_lost(self, exc):
        """On termination."""
        self._connection.setup()

    def write_message(self, message):
        logging.info("Sending message on USB bus: %s, %s", str(message), " ".join(
            [binascii.hexlify(x) for x in message.to_binary()]))
        self._transport.write(message.to_binary())
        time.sleep(float(message.wait_after_send) / float(1000))
        self._connection.controller.new_message(message)


class VelbusUSBConnection(velbus.VelbusConnection):
    # pylint: disable-msg=R0903
    """
    Wrapper for SerialPort connection configuration
    """

    BAUD_RATE = 38400

    BYTE_SIZE = serial.EIGHTBITS

    PARITY = serial.PARITY_NONE

    STOPBITS = serial.STOPBITS_ONE

    XONXOFF = 0

    RTSCTS = 1

    def __init__(self, device):
        velbus.VelbusConnection.__init__(self)
        self._device = device
        self.setup()

    def setup(self):
        loop = asyncio.get_event_loop()
        connection = self

        def coro_done(ftr):
            ftr.result()[1].set_connection(connection)
        coro = serial_asyncio.create_serial_connection(loop, Output,
                                                       self._device,
                                                       baudrate=self.BAUD_RATE,
                                                       bytesize=self.BYTE_SIZE,
                                                       parity=self.PARITY,
                                                       stopbits=self.STOPBITS,
                                                       xonxoff=self.XONXOFF,
                                                       rtscts=self.RTSCTS)
        loop.create_task(coro).add_done_callback(coro_done)

    def set_protocol(self, protocol):
        self._protocol = protocol

    def stop(self):
        logging.warning("Stop executed")
        self._protocol._transport.serial().close()
        time.sleep(1)

    def feed_parser(self, data):
        assert isinstance(data, bytes)
        self.controller.feed_parser(data)

    def send(self, message):
        """
        @return: None
        """
        assert isinstance(message, velbus.Message)
        self._protocol.write_message(message)
