"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import json
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0x00


class PushButtonStatusMessage(Message):
    """
    send by: VMB6IN, VMB4RYLD
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.closed = []
        self.opened = []
        self.closed_long = []
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_high_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 3)
        self.set_attributes(priority, address, rtr)
        self.closed = self.byte_to_channels(data[0])
        self.opened = self.byte_to_channels(data[1])
        self.closed_long = self.byte_to_channels(data[2])

    def set_defaults(self, address):
        if address is not None:
            self.set_address(address)
        self.set_high_priority()
        self.set_no_rtr()

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["closed_channels"] = self.closed
        json_dict["opened_channels"] = self.opened
        json_dict["closed_long_channels"] = self.closed_long
        return json.dumps(json_dict)

    def get_channels(self):
        """
        :return: list
        """
        return self.closed + self.opened

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes(
            [
                COMMAND_CODE,
                self.channels_to_byte(self.closed),
                self.channels_to_byte(self.opened),
                self.channels_to_byte(self.closed_long),
            ]
        )


register_command(COMMAND_CODE, PushButtonStatusMessage)
