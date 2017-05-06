"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import json
import logging

COMMAND_CODE = 0x01


class SwitchRelayOffMessage(velbus.Message):
    """
    send by:
    received by: VMB4RYLD
    """
    # pylint: disable-msg=R0904

    def __init__(self):
        velbus.Message.__init__(self)
        self.relay_channels = []

    def populate(self, priority, address, rtr, data):
        """
        @return: None
        """
        assert isinstance(data, bytes)
        logging.debug("Populating message: priority %s, address: %s, channels: %s", str(
            priority), str(address), str(data))
        self.needs_high_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 1)
        self.set_attributes(priority, address, rtr)
        logging.debug("Setting relay channels to %s",
                      str(self.byte_to_channels(data)))
        self.relay_channels = self.byte_to_channels(data)

    def to_json(self):
        """
        @return: str
        """
        json_dict = self.to_json_basic()
        json_dict['channels'] = self.relay_channels
        return json.dumps(json_dict)

    def set_defaults(self, address):
        self.set_address(address)
        self.set_high_priority()
        self.set_no_rtr()

    def data_to_binary(self):
        """
        @return: bytes
        """
        return bytes([
            COMMAND_CODE,
            self.channels_to_byte(self.relay_channels)
        ])

velbus.register_command(COMMAND_CODE, SwitchRelayOffMessage)
