"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
import velbus

COMMAND_CODE = 0xff

MODULE_DIRECTORY = {
    0x01: 'VMB8PB',
    0x02: 'VMB1RY',
    0x03: 'VMB1BL',
    0x05: 'VMB6IN',
    0x07: 'VMB1DM',
    0x08: 'VMB4RY',
    0x09: 'VMB2BL',
    0x0a: 'VMB8IR',
    0x0b: 'VMB4PD',
    0x0c: 'VMB1TS',
    0x0d: 'VMB1TH',
    0x0e: 'VMB1TC',
    0x0f: 'VMB1LED',
    0x10: 'VMB4RYLD',
    0x11: 'VMB4RYNO',
    0x12: 'VMB4DC',
    0x13: 'VMBLCDWB',
    0x14: 'VMBDME',
    0x15: 'VMBDMI',
    0x16: 'VMB8PBU',
    0x17: 'VMB6PBN',
    0x18: 'VMB2PBN',
    0x19: 'VMB6PBB',
    0x1a: 'VMB4RF',
    0x1b: 'VMB1RYNO',
    0x1c: 'VMB1BLE',
    0x1d: 'VMB2BLE',
    0x1e: 'VMBGP1',
    0x1f: 'VMBGP2',
    0x20: 'VMBGP4',
    0x21: 'VMBGP0',
    0x22: 'VMB7IN',
    0x28: 'VMBGPOD',
    0x29: 'VMB1RYNOS',
    0x2a: 'VMBIRM',
    0x2b: 'VMBIRC',
    0x2c: 'VMBIRO',
    0x2d: 'VMBGP4PIR',
    0x2e: 'VMB1BLS',
    0x2f: 'VMBDMI-R',
    0x31: 'VMBMETEO',
    0x32: 'VMB4AN',

}


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
        self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.module_type = data[0]
        (self.serial,) = struct.unpack(
            '>L', bytes([0, 0, data[1], data[2]]))
        self.memory_map_version = data[3]
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
