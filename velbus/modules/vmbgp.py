"""
:author: Thomas Delaet <thomas@delaet.org
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.temp_sensor_status import TempSensorStatusMessage
from velbus.messages.sensor_temperature import SensorTemperatureMessage
from velbus.messages.push_button_status import PushButtonStatusMessage
from velbus.messages.module_status import ModuleStatusMessage2
from velbus.messages.switch_to_safe import SwitchToSafeMessage
from velbus.messages.switch_to_night import SwitchToNightMessage
from velbus.messages.switch_to_day import SwitchToDayMessage
from velbus.messages.switch_to_comfort import SwitchToComfortMessage
from velbus.messages.set_temperature import SetTemperatureMessage

class VMBGPxModule(Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._cur = None
        self._min = None
        self._max = None
        self._callbacks = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def is_enabled(self, channel):
        if channel in self._is_enabled:
            return self._is_enabled[channel]
        return False

    def getMinTemp(self):
        return self._min

    def getMiaxTemp(self):
        return self._max

    def getCurTemp(self):
        return self._cur

    def number_of_channels(self):
        # 1-8 = inputs
        # 9 = temp sensor
        return 9

    def _on_message(self, message):
        if isinstance(message, SensorTemperatureMessage):
            self._cur = message.cur
            self._min = message.min
            self._max = message.max
            if 9 in self._callbacks:
                for callback in self._callbacks[9]:
                    callback(message.getCurTemp())
        elif isinstance(message, PushButtonStatusMessage):
            for channel in message.closed:
                self._is_closed[channel] = True
            for channel in message.opened:
                self._is_closed[channel] = False
            for channel in message.get_channels():
                if channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._is_closed[channel])
        elif isinstance(message, ModuleStatusMessage2):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.closed:
                    self._is_closed[channel] = True
                else:
                    self._is_closed[channel] = False
                if channel in message.enabled:
                    self._is_enabled[channel] = True
                else:
                    self._is_enabled[channel] = False
            if channel in self._callbacks:
                for callback in self._callbacks[channel]:
                    callback(self._is_closed[channel])

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        if channel == 9:
            return ['sensor']
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ['binary_sensor']
        else:
            return []

    def get_state(self, channel):
        """
        Can only be called for channel 9
        So ignore channel
        """
        return self._cur

    def get_class(self, channel):
        """
        Can only be called for channel 9
        So ignore channel
        """
        return 'temperature'

    def get_unit(self, channel):
        """
        Can only be called for channel 9
        So ignore channel
        """
        return '°C'


class VMBGPxDModule(VMBGPxModule):

    def __init__(self, module_type, module_name, module_address, controller):
        VMBGPxModule.__init__(self, module_type, module_name, module_address, controller)
        self._cmode = None
        self._target = None

    def _on_message(self, message):
        if isinstance(message, TempSensorStatusMessage):
            self._cur = message.current_temp
            self._target = message.target_temp
            self._cmode = message.mode_str
            self._cstatus = message.status_str
            if 33 in self._callbacks:
                for callback in self._callbacks[33]:
                    callback(message.getCurTemp())
        VMBGPxModule._on_message(self, message)

    def get_categories(self, channel):
        if channel == 33:
            return ['sensor', 'climate']
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ['binary_sensor']
        else:
            return []

    def get_climate_mode(self):
        return self._cmode

    def get_climate_target(self):
        return self._target

    def set_mode(self, mode):
        if mode == "safe":
            message = SwitchToSafeMessage(self._address)
        elif mode == "night":
            message = SwitchToNightMessage(self._address)
        elif mode == "day":
            message = SwitchToDayMessage(self._address)
        elif mode == "comfort":
            message = SwitchToComfortMessage(self._address)
        self._controller.send(message)

    def set_temp(self, temp):
        message = SetTemperatureMessage(self._address)
        message.temp = temp * 2
        self._controller.send(message)

    def number_of_channels(self):
        return 33


class VMBGPPirModule(VMBGPxModule):
    def number_of_channels(self):
        # 1-4 = buttons
        # 5 = dark/light
        # 6 = Motion
        # 7 = light dependant motion
        # 8 = absece
        # 9 = temperature
        return 9

    def get_categories(self, channel):
        if channel == 9:
            return ['sensor']
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ['binary_sensor']
        else:
            return []


register_module('VMBGP1', VMBGPxModule)
register_module('VMBGP2', VMBGPxModule)
register_module('VMBGP4', VMBGPxModule)
register_module('VMBGP0', VMBGPxDModule)
register_module('VMBGPOD', VMBGPxDModule)
register_module('VMBGP4PIR', VMBGPPirModule)
