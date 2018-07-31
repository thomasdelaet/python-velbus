"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import json

COMMAND_CODE = 0xed

#FIXME: This is written for VMB6IN but VMB7IN transmits a different type of of module status message

class ModuleStatusMessage(velbus.Message):
    """
    send by: VMB6IN
    received by:
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.closed = []
        self.led_on = []
        self.led_slow_blinking = []
        self.led_fast_blinking = []
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 4)
        self.set_attributes(priority, address, rtr)
        self.closed = self.byte_to_channels(data[0])
        self.led_on = self.byte_to_channels(data[1])
        self.led_slow_blinking = self.byte_to_channels(data[2])
        self.led_fast_blinking = self.byte_to_channels(data[3])

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.channels_to_byte(self.closed),
            self.channels_to_byte(self.led_on),
            self.channels_to_byte(self.led_slow_blinking),
            self.channels_to_byte(self.led_fast_blinking)
        ])

class ModuleStatusMessage2(velbus.Message):

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.closed = []
        self.enabled = []
        self.normal = []
        self.locked = []
        self.programenabled = []

    def populate(self, priority, address, rtr, data):
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.closed = self.byte_to_channels(data[0])
        self.enabled = self.byte_to_channels(data[1])
        self.normal = self.byte_to_channels(data[2])
        self.locked = self.byte_to_channels(data[3])
        self.programenabled = self.byte_to_channels(data[4])

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.channels_to_byte(self.closed),
            self.channels_to_byte(self.enabled),
            self.channels_to_byte(self.normal),
            self.channels_to_byte(self.locked)
        ])

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict['closed'] = self.closed
        json_dict['enabled'] = self.enabled
        json_dict['normal'] = self.normal
        json_dict['locked'] = self.locked
        return json.dumps(json_dict)


velbus.register_command(COMMAND_CODE, ModuleStatusMessage)
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMB8PBU')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMB6PBN')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMB2PBN')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMB6PBB')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMBGP1')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMBGP2')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMBGP4')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMBGP0')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMBGPOD')
velbus.register_command(COMMAND_CODE, ModuleStatusMessage2, 'VMB7IN')
