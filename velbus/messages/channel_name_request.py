"""
:author: Thomas Delaet <thomas@delaet.org> and Maikel Punie <maikel.punie@gmail.com>
"""
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xEF


class ChannelNameRequestMessage(Message):
    """
    send by:
    received by: VMB6IN, VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.channels = []
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 1)
        self.set_attributes(priority, address, rtr)
        self.channels = self.byte_to_channels(data[0])

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE, self.channels_to_byte(self.channels)])


class ChannelNameRequestMessage2(ChannelNameRequestMessage):
    """
    send by:
    received by: VMB2BL
    """

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 1)
        self.set_attributes(priority, address, rtr)
        tmp = (data[0] >> 1) & 0x03
        self.channels = self.byte_to_channels(tmp)

    def data_to_binary(self):
        """
        :return: bytes
        """
        tmp = 0x00
        if 1 in self.channels:
            tmp += 0x03
        if 2 in self.channels:
            tmp += 0x0C
        return bytes([COMMAND_CODE, tmp])


register_command(COMMAND_CODE, ChannelNameRequestMessage)
