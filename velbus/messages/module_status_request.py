"""
:author: Thomas Delaet <thomas@delaet.org>
"""
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xFA


class ModuleStatusRequestMessage(Message):
    """
    send by:
    received by: VMB6IN, VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.channels = []
        self.wait_after_send = 500
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


register_command(COMMAND_CODE, ModuleStatusRequestMessage)
