"""
:author: Tom Dupré <gitd8400@gmail.com>
"""
import json
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xEC
DSTATUS = {0: "off", 1: "up", 2: "down"}


class BlindStatusNgMessage(Message):
    """
    sent by: VMB2BLE
    received by:
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.channel = 0
        self.timeout = 0
        self.status = 0
        self.position = None
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 7)
        self.set_attributes(priority, address, rtr)
        self.channel = self.byte_to_channel(data[0])
        self.needs_valid_channel(self.channel, 5)
        self.timeout = data[1]  # Omzetter seconden ????
        self.status = data[2]
        self.position = data[4]

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["channel"] = self.channel
        json_dict["timeout"] = self.timeout
        json_dict["status"] = DSTATUS[self.status]
        return json.dumps(json_dict)

    def is_up(self):
        """
        :return: bool
        """
        return self.status == 0x01

    def is_down(self):
        """
        :return: bool
        """
        return self.status == 0x02

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes(
            [
                COMMAND_CODE,
                self.channels_to_byte([self.channel]),
                self.timeout,
                self.status,
                self.led_status,
                self.blind_position,
                self.locked_inhibit_forced,
                self.alarm_auto_mode_selection,
            ]
        )


class BlindStatusMessage(Message):
    """
    sent by: VMB2BLE
    received by:
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.channel = 0
        self.timeout = 0
        self.status = 0
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 7)
        self.set_attributes(priority, address, rtr)
        # 00000011 = channel 1
        # 00001100 = channel 2
        # so shift 1 bit to the right + and with 03
        tmp = (data[0] >> 1) & 0x03
        self.channel = self.byte_to_channel(tmp)
        self.needs_valid_channel(self.channel, 5)
        self.timeout = data[1]  # Omzetter seconden ????
        # 2 bits per channel used
        self.status = data[2] >> ((self.channel - 1) * 2)

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["channel"] = self.channel
        json_dict["timeout"] = self.timeout
        json_dict["status"] = DSTATUS[self.status]
        return json.dumps(json_dict)

    def is_up(self):
        """
        :return: bool
        """
        return self.status == 0x01

    def is_down(self):
        """
        :return: bool
        """
        return self.status == 0x02


register_command(COMMAND_CODE, BlindStatusNgMessage, "VMB1BLE")
register_command(COMMAND_CODE, BlindStatusNgMessage, "VMB2BLE")
register_command(COMMAND_CODE, BlindStatusMessage, "VMB1BL")
register_command(COMMAND_CODE, BlindStatusMessage, "VMB2BL")
