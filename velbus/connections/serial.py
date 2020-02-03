"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import time
import threading
import logging
from queue import Queue
import serial
import serial.threaded
from velbus.connections.connection import VelbusConnection
from velbus.util import VelbusException
from velbus.message import Message
from velbus.constants import SLEEP_TIME


class Protocol(serial.threaded.Protocol):
    """Serial protocol."""

    def data_received(self, data):
        # pylint: disable-msg=E1101
        self.parser(data)


class VelbusUSBConnection(VelbusConnection):
    """
    Wrapper for SerialPort connection configuration
    """

    BAUD_RATE = 38400

    BYTE_SIZE = serial.EIGHTBITS

    PARITY = serial.PARITY_NONE

    STOPBITS = serial.STOPBITS_ONE

    XONXOFF = 0

    RTSCTS = 1

    def __init__(self, device, controller=None):
        VelbusConnection.__init__(self)
        self.logger = logging.getLogger("velbus")
        self._device = device
        self.controller = controller
        try:
            self.serial = serial.Serial(
                port=device,
                baudrate=self.BAUD_RATE,
                bytesize=self.BYTE_SIZE,
                parity=self.PARITY,
                stopbits=self.STOPBITS,
                xonxoff=self.XONXOFF,
                rtscts=self.RTSCTS,
            )
        except serial.serialutil.SerialException:
            self.logger.error(
                "Could not open serial port, \
                              no messages are read or written to the bus"
            )
            raise VelbusException("Could not open serial port")
        self._reader = serial.threaded.ReaderThread(self.serial, Protocol)
        self._reader.start()
        self._reader.protocol.parser = self.feed_parser
        self._reader.connect()
        self._write_queue = Queue()
        self._write_process = threading.Thread(
            None, self.write_daemon, "write_packets_process", (), {}
        )
        self._write_process.daemon = True
        self._write_process.start()

    def stop(self):
        """Close serial port."""
        self.logger.warning("Stop executed")
        try:
            self._reader.close()
        except serial.serialutil.SerialException:
            self.logger.error("Error while closing device")
            raise VelbusException("Error while closing device")
        time.sleep(1)

    def feed_parser(self, data):
        """Parse received message."""
        assert isinstance(data, bytes)
        self.controller.feed_parser(data)

    def send(self, message, callback=None):
        """Add message to write queue."""
        assert isinstance(message, Message)
        self._write_queue.put_nowait((message, callback))

    def write_daemon(self):
        """Write thread."""
        while True:
            (message, callback) = self._write_queue.get(block=True)
            self.logger.info("Sending message on USB bus: %s", str(message))
            self.logger.debug("Sending binary message:  %s", str(message.to_binary()))
            self._reader.write(message.to_binary())
            time.sleep(SLEEP_TIME)
            if callback:
                callback()
