"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0x03


class StartRelayTimerMessage(Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.relay_channels = []
        self.delay_time = 0
        self.set_defaults(address)

    def set_defaults(self, address):
        if address is not None:
            self.set_address(address)
        self.set_high_priority()
        self.set_no_rtr()

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_high_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 4)
        self.set_attributes(priority, address, rtr)
        self.relay_channels = self.byte_to_channels(data)
        (self.delay_time,) = struct.unpack(">L", bytes([0]) + data[1:])

    def data_to_binary(self):
        """
        :return: bytes
        """
        return (
            bytes([COMMAND_CODE, self.channels_to_byte(self.relay_channels)])
            + struct.pack(">L", self.delay_time)[-3:]
        )


register_command(COMMAND_CODE, StartRelayTimerMessage)
