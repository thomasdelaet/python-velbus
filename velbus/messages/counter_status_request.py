"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import velbus

COMMAND_CODE = 0xbd


class CounterStatusRequestMessage(velbus.Message):
    """
    send by:
    received by: VMB7IN
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
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

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            0x0f,
            0x00
        ])


velbus.register_command(COMMAND_CODE, CounterStatusRequestMessage, 'VMB7IN')
