"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xf4


class UpdateLedStatusMessage(velbus.Message):
    """
    send by:
    received by: VMB6IN
    """

    def __init__(self):
        velbus.Message.__init__(self)
        self.led_on = []
        self.led_slow_blinking = []
        self.led_fast_blinking = []

    def populate(self, priority, address, rtr, data):
        """
        @return None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 3)
        self.set_attributes(priority, address, rtr)
        self.led_on = self.byte_to_channels(data[0])
        self.led_slow_blinking = self.byte_to_channels(data[1])
        self.led_fast_blinking = self.byte_to_channels(data[2])

    def data_to_binary(self):
        """
        @return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.channels_to_byte(self.led_on),
            self.channels_to_byte(self.led_slow_blinking),
            self.channels_to_byte(self.led_fast_blinking)
        ])


velbus.register_command(COMMAND_CODE, UpdateLedStatusMessage)
