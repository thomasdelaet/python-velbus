"""
:author: Thomas Delaet <thomas@delaet.org>
"""
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0x0C


class ReceiveReadyMessage(Message):
    """
    send by:
    received by: VMB1USB
    """

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        # self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_no_data(data)
        self.set_attributes(priority, address, rtr)

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE])


register_command(COMMAND_CODE, ReceiveReadyMessage)
