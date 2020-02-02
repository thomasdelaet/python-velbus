"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import json
import logging
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0x02


class SwitchRelayOnMessage(Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.relay_channels = []
        self.logger = logging.getLogger("velbus")
        self.set_defaults(address)

    def set_defaults(self, address):
        if address is not None:
            self.set_address(address)
        self.set_high_priority()
        self.set_no_rtr()

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_high_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 1)
        self.set_attributes(priority, address, rtr)
        self.relay_channels = self.byte_to_channels(data[0])

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["channels"] = self.relay_channels
        return json.dumps(json_dict)

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE, self.channels_to_byte(self.relay_channels)])


register_command(COMMAND_CODE, SwitchRelayOnMessage)
