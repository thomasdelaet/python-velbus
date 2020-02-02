"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import struct
from velbus.message import Message
from velbus.command_registry import register_command


COMMAND_CODE = 0x6A


class WriteModuleAddressAndSerialNumberMessage(Message):
    """
    send by:
    received by: VMB4RYLD
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.module_type = 0x00
        self.current_serial = 0
        self.module_address = 0x00
        self.new_serial = 0
        self.set_defaults(address)

    def set_defaults(self, address):
        if address is not None:
            self.set_address(address)
        self.set_firmware_priority()
        self.set_no_rtr()

    def populate(self, priority, address, rtr, data):
        """
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_firmware_priority(priority)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        self.module_type = data[0]
        prefix = bytes([0, 0])
        (self.current_serial,) = struct.unpack(">L", prefix + data[1] + data[2])
        self.module_address = data[3]
        (self.new_serial,) = struct.unpack(">L", prefix + data[4] + data[5])

    def data_to_binary(self):
        """
        :return: bytes
        """
        return (
            chr(COMMAND_CODE)
            + chr(self.module_type)
            + struct.pack(">L", self.current_serial)[2:]
            + chr(self.module_address)
            + struct.pack(">L", self.new_serial)[2:]
        )


register_command(COMMAND_CODE, WriteModuleAddressAndSerialNumberMessage)
