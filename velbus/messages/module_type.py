"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
import velbus

COMMAND_CODE = 0xff

class ModuleTypeMessage(velbus.Message):
    """
    send by: VMB6IN, VMB4RYLD
    received by:
    """
    #pylint: disable-msg=R0902

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.module_type = 0x00
        self.led_on = []
        self.led_slow_blinking = []
        self.led_fast_blinking = []
        self.serial = 0
        self.memory_map_version = 0
        self.build_year = 0
        self.build_week = 0
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
        self.needs_data(data, 4)
        self.set_attributes(priority, address, rtr)
        self.module_type = data[0]
        (self.serial,) = struct.unpack(
            '>L', bytes([0, 0, data[1], data[2]]))
        self.memory_map_version = data[3]
        if len(data) > 4:
            self.build_year = data[4]
            self.build_week = data[5]

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.module_type,
            self.channels_to_byte(self.led_on),
            self.channels_to_byte(self.led_slow_blinking),
            self.channels_to_byte(self.led_fast_blinking),
            self.build_year,
            self.build_week
        ])


velbus.register_command(COMMAND_CODE, ModuleTypeMessage)
