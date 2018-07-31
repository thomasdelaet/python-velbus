"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
import velbus
import json

COMMAND_CODE = 0xb0

class ModuleSubTypeMessage(velbus.Message):
    """
    send by: VMB6IN, VMB4RYLD
    received by:
    """
    #pylint: disable-msg=R0902

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.module_type = 0x00
        self.sub_address_1 = 0xff
        self.sub_address_2 = 0xff
        self.sub_address_3 = 0xff
        self.sub_address_4 = 0xff
        self.set_defaults(address)

    def module_name(self):
        """
        :return: str
        """
        if self.module_type in velbus.MODULE_DIRECTORY.keys():
            return velbus.MODULE_DIRECTORY[self.module_type]
        return "Unknown"

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        #self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.module_type = data[0]
        self.sub_address_1 = data[3]
        self.sub_address_2 = data[4]
        self.sub_address_3 = data[5]
        self.sub_address_4 = data[6]


    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict['sub_1'] = self.sub_address_1
        json_dict['sub_2'] = self.sub_address_2
        json_dict['sub_3'] = self.sub_address_3
        json_dict['sub_4'] = self.sub_address_4
        return json.dumps(json_dict)

velbus.register_command(COMMAND_CODE, ModuleSubTypeMessage, 'VMBGP1')
velbus.register_command(COMMAND_CODE, ModuleSubTypeMessage, 'VMBGP2')
velbus.register_command(COMMAND_CODE, ModuleSubTypeMessage, 'VMBGP4')
velbus.register_command(COMMAND_CODE, ModuleSubTypeMessage, 'VMBGP0')
velbus.register_command(COMMAND_CODE, ModuleSubTypeMessage, 'VMBGPOD')

