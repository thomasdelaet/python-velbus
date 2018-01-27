"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xca


class WriteMemoryBlockMessage(velbus.Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.high_address = 0x00
        self.low_address = 0x00
        self.data = ""
        self.set_defaults(address)

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_low_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.high_address = data[0]
        self.low_address = data[1]
        self.data = data[2:]

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([COMMAND_CODE, self.high_address, self.low_address] + self.data)


velbus.register_command(COMMAND_CODE, WriteMemoryBlockMessage)
