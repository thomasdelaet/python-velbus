"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import json
from velbus.message import Message
from velbus.command_registry import register_command

COMMAND_CODE = 0xE6


class SensorTemperatureMessage(Message):
    """
    send by: VMBTS, vmbg*pd, ...
    received by:
    """

    def __init__(self, address=None):
        Message.__init__(self)
        self.cur = 0
        self.min = 0
        self.max = 0

    def getCurTemp(self):
        return self.cur

    def populate(self, priority, address, rtr, data):
        """
        data bytes (high + low)
            1 + 2   = current temp
            3 + 4   = min temp
            5 + 6   = max temp
        :return: None
        """
        assert isinstance(data, bytes)
        self.needs_no_rtr(rtr)
        self.needs_data(data, 6)
        self.set_attributes(priority, address, rtr)
        if ((data[0] << 8) | data[1]) >> 15:
            self.cur = -127 + (((data[0] << 8) | data[1]) / 32 * 0.0625)
        else:
            self.cur = (((data[0] << 8) | data[1]) / 32) * 0.0625
        if ((data[2] << 8) | data[3]) >> 15:
            self.min = -127 + (((data[2] << 8) | data[3]) / 32 * 0.0625)
        else:
            self.min = (((data[2] << 8) | data[3]) / 32) * 0.0625
        if ((data[4] << 8) | data[5]) >> 15:
            self.max = -127 + (((data[4] << 8) | data[5]) / 32 * 0.0625)
        else:
            self.max = (((data[4] << 8) | data[5]) / 32) * 0.0625

    def to_json(self):
        """
        :return: str
        """
        json_dict = self.to_json_basic()
        json_dict["cur"] = self.cur
        json_dict["min"] = self.min
        json_dict["max"] = self.max
        return json.dumps(json_dict)


register_command(COMMAND_CODE, SensorTemperatureMessage)
