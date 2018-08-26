"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import json
import logging
import velbus

COMMAND_CODE = 0xdf


class TempSetCoolingMessage(velbus.Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
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
        return bytes([
            COMMAND_CODE,
            0xaa
        ])

velbus.register_command(COMMAND_CODE, TempSetCoolingMessage)
