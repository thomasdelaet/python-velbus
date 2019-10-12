"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import json
import logging
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xE0


class TempSetHeatingMessage(Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        self.needs_no_rtr(rtr)
        self.set_attributes(priority, address, rtr)

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        return json.dumps(json_dict)

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE, 0xAA])


register_command(COMMAND_CODE, TempSetHeatingMessage)
