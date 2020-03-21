"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import base64
from velbus.connections.connection import VelbusConnection
from velbus.message import Message
import paho.mqtt.client as mqtt


class VelbusMQTTConnection(VelbusConnection):
    """
    Wrapper for MQTT connection configuration
    :author: Thomas Delaet <thomas@delaet.org>
    """

    def __init__(self, device, controller=None):
        VelbusConnection.__init__(self)
        self.logger = logging.getLogger("velbus")
        self._device = device
        self.controller = controller
        # get the address from a <host>:<port> format
        addr = device.split(":")
        addr = (addr[0], int(addr[1]))
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(addr[0], addr[1])
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        self.client.subscribe('velbus')

    def _on_message(self, client, userdata, msg):
        self.feed_parser(bytes(base64.b64decode(msg.payload)))

    def stop(self):
        """Close the socket."""
        self.logger.warning("Stop executed")
        self.client.disconnect()
        self.client.loop_stop()

    def feed_parser(self, data):
        """Parse received message."""
        assert isinstance(data, bytes)
        self.controller.feed_parser(data)

    def send(self, message, callback=None):
        """Add message to write queue."""
        assert isinstance(message, Message)
        self.client.publish('velbus/send', payload=message.to_base64())
