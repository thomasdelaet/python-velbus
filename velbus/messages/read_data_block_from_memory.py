"""
:author: Thomas Delaet <thomas@delaet.org>
"""
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xC9


class ReadDataBlockFromMemoryMessage(Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.high_address = 0x00
        self.low_address = 0x00
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 2)
        self.set_attributes(priority, address, rtr)
        self.low_address = data[1]
        self.high_address = data[0]

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE, self.high_address, self.low_address])


register_command(COMMAND_CODE, ReadDataBlockFromMemoryMessage)
