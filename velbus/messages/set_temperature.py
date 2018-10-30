"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import velbus

COMMAND_CODE = 0xe4


class SetTemperatureMessage(velbus.Message):
    """
    send by: VMB4RYLD
    received by: VMB6IN
    """

    def __init__(self, address=None):
        velbus.Message.__init__(self)
        self.temp_type = 0x00
        self.temp = 0x00
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

        self.temp_type = 0x00
        self.temp = data[1] * 2

    def data_to_binary(self):
        """
        :return: bytes
        """
        return bytes([
            COMMAND_CODE,
            int(self.temp_type),
            int(self.temp)
        ])


velbus.register_command(COMMAND_CODE, SetTemperatureMessage)
