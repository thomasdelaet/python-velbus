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
from velbus.messages.update_led_status import UpdateLedStatusMessage
from velbus.messages.set_led import SetLedMessage
from velbus.messages.slow_blinking_led import SlowBlinkingLedMessage
from velbus.messages.fast_blinking_led import FastBlinkingLedMessage
from velbus.messages.clear_led import ClearLedMessage
from velbus.messages.memo_text import MemoTextMessage


class VMBGPxModule(Module):
    """
    Velbus input module with 32 input channels and 1 temperature sensor
    Input channel 9 up to 32 are addressable by sub modules
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._led_state = {}
        self._cur = None
        self._min = None
        self._max = None
        self._callbacks = {}
        self._controllable_channels = 8
        self._temperature_channel = 33

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

    def getMaxTemp(self):
        return self._max

    def getCurTemp(self):
        return self._cur

    def number_of_channels(self):
        # 1-32 = inputs
        # 33 = temperature sensor
        return 33

    def _on_message(self, message):
        if isinstance(message, SensorTemperatureMessage):
            self._cur = message.cur
            self._min = message.min
            self._max = message.max
            if self._temperature_channel in self._callbacks:
                for callback in self._callbacks[self._temperature_channel]:
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
            for channel in list(range(1, self._controllable_channels + 1)):
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
        elif isinstance(message, UpdateLedStatusMessage):
            for channel in list(range(1, self._controllable_channels + 1)):
                self._led_state[channel] = "off"
                if channel in message.led_slow_blinking:
                    self._led_state[channel] = "slow"
                if channel in message.led_fast_blinking:
                    self._led_state[channel] = "fast"
                if channel in message.led_on:
                    self._led_state[channel] = "on"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, SetLedMessage):
            for channel in list(range(1, self._controllable_channels + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "on"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, ClearLedMessage):
            for channel in list(range(1, self._controllable_channels + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "off"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, SlowBlinkingLedMessage):
            for channel in list(range(1, self._controllable_channels + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "slow"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, FastBlinkingLedMessage):
            for channel in list(range(1, self._controllable_channels + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "fast"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])

    def is_on(self, channel):
        """
        Check if led of channel is turned on

        :return: bool
        """
        if channel in self._led_state:
            if self._led_state[channel] == "off":
                return False
            else:
                return True
        return False

    def set_led_state(self, channel, state, callback=None):
        """
        Set led

        :return: None
        """
        if callback is None:

            def callb():
                """No-op"""
                pass

            callback = callb
        if state == "on":
            message = SetLedMessage(self._address)
        elif state == "slow":
            message = SlowBlinkingLedMessage(self._address)
        elif state == "fast":
            message = FastBlinkingLedMessage(self._address)
        elif state == "off":
            message = ClearLedMessage(self._address)
        else:
            return
        message.leds = [channel]
        self._led_state[channel] = state
        self._controller.send(message, callback)

    def light_is_buttonled(self, channel):
        return True

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        if channel == self._temperature_channel:
            return ["sensor"]
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ["binary_sensor", "light"]
        else:
            return []

    def get_state(self, channel):
        """
        Can only be called for channel 33
        So ignore channel
        """
        return self._cur

    def get_class(self, channel):
        """
        Can only be called for channel 33
        So ignore channel
        """
        return "temperature"

    def get_unit(self, channel):
        """
        Can only be called for channel 33
        So ignore channel
        """
        return "°C"

    def set_memo_text(self, text_message=""):
        """
        set the memo text
        Empty message clears memo
        """
        assert isinstance(text_message, str)
        assert len(text_message) <= 64
        message = MemoTextMessage(self._address)
        msgcntr = 0
        for char in text_message:
            message.memo_text += char
            if len(message.memo_text) >= 5:
                msgcntr += 5
                self._controller.send(message)
                message = MemoTextMessage(self._address)
                message.start = msgcntr
        self._controller.send(message)


class VMBGPxSubModule(VMBGPxModule):
    """
    Velbus input sub module with 8 input channels
    """

    def __init__(
        self,
        module_type,
        module_name,
        module_address,
        master_address,
        sub_module,
        controller,
    ):
        VMBGPxModule.__init__(
            self, module_type, module_name, module_address, controller
        )
        self._master_address = master_address
        self.sub_module = sub_module

    def _is_submodule(self):
        return True

    def get_categories(self, channel):
        if channel in self._is_enabled and self._is_enabled[channel]:
            return ["binary_sensor", "light"]
        else:
            return []

    def number_of_channels(self):
        return 8


class VMBGP124Module(VMBGPxModule):
    """
    Velbus VMBGP1, VMBGP2 and VMBGP4 modules
    """

    def __init__(self, module_type, module_name, module_address, controller):
        VMBGPxModule.__init__(
            self, module_type, module_name, module_address, controller
        )
        self._temperature_channel = 9

    def number_of_channels(self):
        # 1-8 = inputs
        # 9 = temperature sensor
        return 9


class VMBGPxDModule(VMBGPxModule):
    def __init__(self, module_type, module_name, module_address, controller):
        VMBGPxModule.__init__(
            self, module_type, module_name, module_address, controller
        )
        self._cmode = None
        self._target = None
        self._temperature_channel = 33

    def _on_message(self, message):
        if isinstance(message, TempSensorStatusMessage):
            self._cur = message.current_temp
            self._target = message.target_temp
            self._cmode = message.mode_str
            self._cstatus = message.status_str
            if self._temperature_channel in self._callbacks:
                for callback in self._callbacks[self._temperature_channel]:
                    callback(message.getCurTemp())
        VMBGPxModule._on_message(self, message)

    def get_categories(self, channel):
        if channel == self._temperature_channel:
            return ["sensor", "climate"]
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ["binary_sensor", "light"]
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
        # 8 = absence
        # 9 = temperature
        return 9

    def get_categories(self, channel):
        if channel == 9:
            return ["sensor"]
        elif channel in self._is_enabled and self._is_enabled[channel]:
            return ["binary_sensor"]
        else:
            return []


register_module("VMBGP1", VMBGP124Module)
register_module("VMBGP1-2", VMBGP124Module)
register_module("VMBEL1", VMBGP124Module)
register_module("VMBGP2", VMBGP124Module)
register_module("VMBGP2-2", VMBGP124Module)
register_module("VMBEL2", VMBGP124Module)
register_module("VMBGP4", VMBGP124Module)
register_module("VMBGP4-2", VMBGP124Module)
register_module("VMBEL4", VMBGP124Module)
register_module("VMBGPO", VMBGPxModule)
register_module("SUB_VMBGPO", VMBGPxSubModule)
register_module("VMBELO", VMBGPxDModule)
register_module("SUB_VMBELO", VMBGPxSubModule)
register_module("VMBGPOD", VMBGPxDModule)
register_module("SUB_VMBGPOD", VMBGPxSubModule)
register_module("VMBGP4PIR", VMBGPPirModule)
