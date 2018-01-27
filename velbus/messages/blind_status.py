"""
:author: Tom Dupré <gitd8400@gmail.com>
"""
import json
import velbus

COMMAND_CODE = 0xEC

CHANNEL_NORMAL = 0x00

CHANNEL_INHIBITED = 0x01

CHANNEL_INHIBITED_PRESET_DOWN = 0x02

CHANNEL_INHIBITED_PRESET_UP = 0x03

CHANNEL_FORCED_DOWN = 0x04

CHANNEL_FORCED_UP = 0x05

CHANNEL_LOCKED = 0x06

BLIND_OFF = 0x00

BLIND_UP = 0x01

BLIND_DOWN = 0x02

LED_OFF = 0

DOWN_LED_ON = 1 << 7

DOWN_LED_SLOW_BLINKING = 1 << 6

DOWN_LED_FAST_BLINKING = 1 << 5

DOWN_LED_VERY_FAST_BLINKING = 1 << 4

UP_LED_ON = 1 << 3

UP_LED_SLOW_BLINKING = 1 << 2

UP_LED_FAST_BLINKING = 1 << 1

UP_LED_VERY_FAST_BLINKING = 1


class BlindStatusMessage(velbus.Message):
    """
    sent by: VMB2BLE
    received by:
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.channel = 0
        self.timeout = 0
        self.status = 0
        self.led_status = 0
        self.blind_position = 0
        self.locked_inhibit_forced = 0
        self.alarm_auto_mode_selection = 0
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
        self.timeout = data[1] # Omzetter seconden ????
        self.status = data[2]
        self.led_status = data[3]
        self.blind_position = data[4]
        self.locked_inhibit_forced = data[5]
        self.alarm_auto_mode_selection = data[6]

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict['channel'] = self.channel
        json_dict['timeout'] = self.timeout
        json_dict['status'] = self.status
        json_dict['led_status'] = self.led_status
        json_dict['blind_position'] = self.blind_position
        json_dict['locked_inhibit_forced'] = self.locked_inhibit_forced
        json_dict['alarm_auto_mode_selection'] = self.alarm_auto_mode_selection
        return json.dumps(json_dict)

    def is_normal(self):
        """
        :return: bool
        """
        return self.locked_inhibit_forced == CHANNEL_NORMAL

    def is_inhibited(self):
        """
        :return: bool
        """
        return self.locked_inhibit_forced == CHANNEL_INHIBITED

    def is_locked(self):
        """
        :return: bool
        """
        return self.locked_inhibit_forced == CHANNEL_LOCKED

    def is_up(self):
        """
        :return: bool
        """
        return self.status == BLIND_UP

    def is_down(self):
        """
        :return: bool
        """
        return self.status == BLIND_OFF

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.channels_to_byte([self.channel]),
            self.timeout,
            self.status,
            self.led_status,
            self.blind_position,
            self.locked_inhibit_forced,
            self.alarm_auto_mode_selection
            ])


velbus.register_command(COMMAND_CODE, BlindStatusMessage)
