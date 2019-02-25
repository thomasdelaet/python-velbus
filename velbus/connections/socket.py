"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import time
import threading
import logging
from queue import Queue
from velbus import VelbusException
import velbus
import socket


class SocketConnection(velbus.VelbusConnection):
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
            self._socket.connect(addr)
        except Exception:
            self.logger.error("Could not open socket, \
                              no messages are read or written to the bus")
            raise VelbusException("Could not open socket port")
        # build a read thread
        self._listen_process = threading.Thread(None, self.read_daemon, "velbus-process-reader", (), {})
        self._listen_process.daemon = True
        self._listen_process.start()

        # build a writer thread
        self._write_queue = Queue()
        self._write_process = threading.Thread(None, self.write_daemon, "velbus-connection-writer", (), {})
        self._write_process.daemon = True
        self._write_process.start()

    def stop(self):
        """Close the socket."""
        self.logger.warning("Stop executed")
        try:
            self._socket.close()
        except Exception:
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
