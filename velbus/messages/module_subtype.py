"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
from velbus.message import Message
from velbus.command_registry import register_command
from velbus.module_registry import MODULE_DIRECTORY
import json

COMMAND_CODE = 0xB0


class ModuleSubTypeMessage(Message):
    """
    send by: VMB6IN, VMB4RYLD
    received by:
    """

    # pylint: disable-msg=R0902

    def __init__(self, address=None):
        Message.__init__(self)
        self.module_type = 0x00
        self.sub_address_1 = 0xFF
        self.sub_address_2 = 0xFF
        self.sub_address_3 = 0xFF
        self.sub_address_4 = 0xFF
        self.set_defaults(address)
        self.serial = 0

    def module_name(self):
        """
        :return: str
        """
        if self.module_type in MODULE_DIRECTORY.keys():
            return MODULE_DIRECTORY[self.module_type]
        return "Unknown"

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        # self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.module_type = data[0]
        (self.serial,) = struct.unpack(">L", bytes([0, 0, data[1], data[2]]))
        self.sub_address_1 = data[3]
        self.sub_address_2 = data[4]
        self.sub_address_3 = data[5]
        self.sub_address_4 = data[6]

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["sub_1"] = self.sub_address_1
        json_dict["sub_2"] = self.sub_address_2
        json_dict["sub_3"] = self.sub_address_3
        json_dict["sub_4"] = self.sub_address_4
        return json.dumps(json_dict)


register_command(COMMAND_CODE, ModuleSubTypeMessage)
