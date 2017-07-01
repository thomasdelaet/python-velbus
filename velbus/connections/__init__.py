"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import time
import velbus
import serial
import serial.threaded
import threading
import logging
from Queue import Queue


class Protocol(serial.threaded.Protocol):

    def data_received(self, data):
        self.parser(data)


class VelbusException(Exception):
    """Velbus Exception."""
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


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

    SLEEP_TIME = 60 / 1000

    def __init__(self, device):
        velbus.VelbusConnection.__init__(self)
        self.logger = logging.getLogger('velbus')
        self._device = device
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
        self._write_process.start()

    def stop(self):
        """Close serial port."""
        self.logger.warning("Stop executed")
        try:
            self._reader.close()
            self._write_process.stop()
        except serial.serialutil.SerialException:
            self.logger.error("Error while closing device")
            raise VelbusException("Error while closing device")
        time.sleep(1)

    def feed_parser(self, data):
        """Parse received message."""
        assert isinstance(data, bytes)
        self.controller.feed_parser(data)

    def send(self, message):
        """Add message to write queue."""
        assert isinstance(message, velbus.Message)
        self._write_queue.put_nowait(message)

    def write_daemon(self):
        """Write thread."""
        while True:
            message = self._write_queue.get(block=True)
            self.logger.info("Sending message on USB bus: %s", str(message))
            self._reader.write(message.to_binary())
            time.sleep(self.SLEEP_TIME)
