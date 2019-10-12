"""
:author: Thomas Delaet <thomas@delaet.org>
"""
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0x0E


class InterfaceStatusRequestMessage(Message):
    """
    send by: VMB1USB
    received by:
    """

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_no_data(data)
        self.set_attributes(priority, address, rtr)

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE])


register_command(COMMAND_CODE, InterfaceStatusRequestMessage)
