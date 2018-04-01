"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import time
import threading
import logging
from queue import Queue
import velbus
import serial
import serial.threaded
import socket

class Protocol(serial.threaded.Protocol):
    """Serial protocol."""

    def data_received(self, data):
        # pylint: disable-msg=E1101
        self.parser(data)


class VelbusException(Exception):
    """Velbus Exception."""
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class VelbusUSBConnection(velbus.VelbusConnection):
    """
    Wrapper for SerialPort connection configuration
    """

    BAUD_RATE = 38400

    BYTE_SIZE = serial.EIGHTBITS

    PARITY = serial.PARITY_NONE

    STOPBITS = serial.STOPBITS_ONE

    XONXOFF = 0

    RTSCTS = 1

    SLEEP_TIME = 60 / 1000

    def __init__(self, device, controller=None):
        velbus.VelbusConnection.__init__(self)
        self.logger = logging.getLogger('velbus')
        self._device = device
        self.controller = controller
        try:
            self.serial = serial.Serial(port=device,
                                        baudrate=self.BAUD_RATE,
                                        bytesize=self.BYTE_SIZE,
                                        parity=self.PARITY,
                                        stopbits=self.STOPBITS,
                                        xonxoff=self.XONXOFF,
                                        rtscts=self.RTSCTS)
        except serial.serialutil.SerialException:
            self.logger.error("Could not open serial port, \
                              no messages are read or written to the bus")
            raise VelbusException("Could not open serial port")
        self._reader = serial.threaded.ReaderThread(self.serial, Protocol)
        self._reader.start()
        self._reader.protocol.parser = self.feed_parser
        self._reader.connect()
        self._write_queue = Queue()
        self._write_process = threading.Thread(None, self.write_daemon,
                                               "write_packets_process", (), {})
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
        assert isinstance(message, velbus.Message)
        self._write_queue.put_nowait((message, callback))

    def write_daemon(self):
        """Write thread."""
        while True:
            (message, callback) = self._write_queue.get(block=True)
            self.logger.info("Sending message on USB bus: %s", str(message))
            self.logger.debug("Sending binary message:  %s", str(message.to_binary()))
            self._reader.write(message.to_binary())
            time.sleep(self.SLEEP_TIME)
            if callback:
                callback()


class VelbusSocketConnection(velbus.VelbusConnection):
    """
    Wrapper for Socket connection configuration
    :author: Maikel Punie <maikel.punie@gmail.com>
    """
    SLEEP_TIME = 60 / 1000

    def __init__(self, device, controller=None):
        velbus.VelbusConnection.__init__(self)
        self.logger = logging.getLogger('velbus')
        self._device = device
        self.controller = controller
        # get the address from a <host>:<port> format
        addr = device.split(':')
        addr = (addr[0], int(addr[1]))
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect( addr )
        except:
            self.logger.error("Could not open socket, \
                              no messages are read or written to the bus")
            raise VelbusException("Could not open socket port")
        # build a read thread
        self._listen_process = threading.Thread(None, self.read_daemon,
                                         "velbus-process-reader", (), {})
        self._listen_process.daemon = True
        self._listen_process.start()

        # build a writer thread
        self._write_queue = Queue()
        self._write_process = threading.Thread(None, self.write_daemon,
                                               "velbus-connection-writer", (), {})
        self._write_process.daemon = True
        self._write_process.start()

    def stop(self):
        """Close serial port."""
        self.logger.warning("Stop executed")
        try:
            self._socket.close()
        except:
            self.logger.error("Error while closing socket")
            raise VelbusException("Error while closing socket")
        time.sleep(1)

    def feed_parser(self, data):
        """Parse received message."""
        assert isinstance(data, bytes)
        self.controller.feed_parser(data)

    def send(self, message, callback=None):
        """Add message to write queue."""
        assert isinstance(message, velbus.Message)
        self._write_queue.put_nowait((message, callback))

    def read_daemon(self):
        """Read thread."""
        while True:
            data = self._socket.recv(9999)
            self.feed_parser(data)

    def write_daemon(self):
        """Write thread."""
        while True:
            (message, callback) = self._write_queue.get(block=True)
            self.logger.info("Sending message on USB bus: %s", str(message))
            self.logger.debug("Sending binary message:  %s", str(message.to_binary()))
            self._socket.send(message.to_binary())
            time.sleep(self.SLEEP_TIME)
            if callback:
                callback()
