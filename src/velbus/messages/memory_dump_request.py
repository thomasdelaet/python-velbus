"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xcb


class MemoryDumpRequestMessage(velbus.Message):
    """
    send by:
    received by: VMB6IN, VMB4RYLD
    """

    def populate(self, priority, address, rtr, data):
        """
        @return: None
        """
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_no_data(data)
        self.set_attributes(priority, address, rtr)

    def data_to_binary(self):
        """
        @return: bytes
        """
        return bytes([COMMAND_CODE])


velbus.register_command(COMMAND_CODE, MemoryDumpRequestMessage)
