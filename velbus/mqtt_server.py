"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import paho.mqtt.client as mqtt
import logging
from velbus.parser import VelbusParser
from velbus.connections.socket import SocketConnection
from velbus.connections.serial import VelbusUSBConnection
import sys


class MQTTServer(object):
    """
    Velbus MQTT Server.
    """

    def __init__(self, port, mqtt_address, mqtt_port):
        self.logger = logging.getLogger("velbus")
        self.parser = VelbusParser(self)
        if ":" in port:
            self.connection = SocketConnection(port, self)
        else:
            self.connection = VelbusUSBConnection(port, self)
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(mqtt_address, mqtt_port)
        self.client.loop_forever()

    def _on_connect(self, client, userdata, flags, rc):
        self.client.subscribe('velbus/send')

    def _on_message(self, client, userdata, msg):
        print(msg.topic + ' ' + str(msg.payload))

    def feed_parser(self, data):
        """
        Feed parser with new data

        :return: None
        """
        assert isinstance(data, bytes)
        self.parser.feed(data)

    def new_message(self, message):
        self.logger.info("New message: " + str(message))
        self.client.publish('velbus', payload=message.to_base64())


if __name__ == "__main__":
    s = MQTTServer(sys.argv[1], sys.argv[2], sys.argv[3])
