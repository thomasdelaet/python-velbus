"""
:author: Thomas Delaet <thomas@delaet.org
"""
import velbus


class VMBGPxModule(velbus.Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
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
        if isinstance(message, velbus.SensorTemperatureMessage):
            self._cur = message.cur
            self._min = message.min
            self._max = message.max
            if 9 in self._callbacks:
                for callback in self._callbacks[9]:
                    callback(message.getCurTemp())
        elif isinstance(message, velbus.PushButtonStatusMessage):
            for channel in message.closed:
                self._is_closed[channel] = True
            for channel in message.opened:
                self._is_closed[channel] = False
            for channel in message.get_channels():
                if channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._is_closed[channel])
        elif isinstance(message, velbus.ModuleStatusMessage2):
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
        if isinstance(message, velbus.TempSensorStatusMessage):
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
            message = velbus.SwitchToSafeMessage(self._address)
        elif mode == "night":
            message = velbus.SwitchToNightMessage(self._address)
        elif mode == "day":
            message = velbus.SwitchToDayMessage(self._address)
        elif mode == "comfort":
            message = velbus.SwitchToComfortMessage(self._address)
        self._controller.send(message)

    def set_temp(self, temp):
        message = velbus.SetTemperatureMessage(self._address)
        message.temp = temp * 2
        self._controller.send(message)

    def number_of_channels(self):
        return 33


class VMBGPPirModule(velbus.Module):
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


velbus.register_module('VMBGP1', VMBGPxModule)
velbus.register_module('VMBGP2', VMBGPxModule)
velbus.register_module('VMBGP4', VMBGPxModule)
velbus.register_module('VMBGP0', VMBGPxDModule)
velbus.register_module('VMBGPOD', VMBGPxDModule)
velbus.register_module('VMBGP4PIR', VMBGPPirModule)
