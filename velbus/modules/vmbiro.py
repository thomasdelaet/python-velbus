"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import velbus

class VMBIROModule(velbus.Module):
    """
    Velbus outdoor PIR sensor
    for now we only support Temperature
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
        self._cur = None
        self._min = None
        self._max = None
        self._callbacks = []

    def getMinTemp(self):
        return self._min

    def getMiaxTemp(self):
        return self._max

    def getCurTemp(self):
        return self._cur

    def _on_message(self, message):
        if isinstance(message, velbus.SensorTemperatureMessage):
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
        return ['sensor']

    def get_state(self, channel):
        """
        Ignore channel
        """
        return self._cur

    def get_class(self, channel):
        """
        Ignore channel
        """
        return 'temperature'

    def get_unit(self, channel):
        """
        Ignore channel
        """
        return '°C'


velbus.register_module('VMBIRO', VMBIROModule)
