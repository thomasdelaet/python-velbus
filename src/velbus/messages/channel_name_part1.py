"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xf0


class ChannelNamePart1Message(velbus.Message):
    """
    send by: VMB6IN, VMB4RYLD
    received by:
    """

    def __init__(self):
        velbus.Message.__init__(self)
        self.channel = 0
        self.name = ""

    def populate(self, priority, address, rtr, data):
        """
        @return None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 7)
        self.set_attributes(priority, address, rtr)
        channels = self.byte_to_channels(data[0])
        self.needs_one_channel(channels)
        self.channel = channels[0]
        self.name = "".join([chr(x) for x in data[1:]])

    def data_to_binary(self):
        """
        @return: bytes
        """
        return bytes([
                COMMAND_CODE,
                self.channels_to_byte([self.channel])
                ]) + bytes(self.name, 'utf-8')


velbus.register_command(COMMAND_CODE, ChannelNamePart1Message)
