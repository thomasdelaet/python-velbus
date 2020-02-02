"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.sensor_temperature import SensorTemperatureMessage


class VMB1TSModule(Module):
    """
    Velbus input module with 6 channels
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._cur = None
        self._min = None
        self._max = None
        self._callbacks = []

    def getMinTemp(self):
        return self._min

    def getMaxTemp(self):
        return self._max

    def getCurTemp(self):
        return self._cur

    def _on_message(self, message):
        if isinstance(message, SensorTemperatureMessage):
            self._cur = message.cur
            self._min = message.min
            self._max = message.max
            for callback in self._callbacks:
                callback(message.getCurTemp())

    def number_of_channels(self):
        return 1

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        self._callbacks.append(callback)

    def get_categories(self, channel):
        return ["sensor"]

    def get_state(self, channel):
        """
        Ignore channel
        """
        return self._cur

    def get_class(self, channel):
        """
        Ignore channel
        """
        return "temperature"

    def get_unit(self, channel):
        """
        Ignore channel
        """
        return "°C"


register_module("VMB1TS", VMB1TSModule)
