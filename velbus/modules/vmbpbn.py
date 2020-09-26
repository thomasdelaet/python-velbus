"""
:author: Thomas Delaet <thomas@delaet.org
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.push_button_status import PushButtonStatusMessage
from velbus.messages.module_status import ModuleStatusMessage2
from velbus.messages.update_led_status import UpdateLedStatusMessage
from velbus.messages.set_led import SetLedMessage
from velbus.messages.slow_blinking_led import SlowBlinkingLedMessage
from velbus.messages.fast_blinking_led import FastBlinkingLedMessage
from velbus.messages.clear_led import ClearLedMessage


class VMB2PBNModule(Module):
    """
    Velbus input module with 2 channels
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._callbacks = {}
        self._led_state = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def number_of_channels(self):
        return 2

    def _on_message(self, message):
        if isinstance(message, PushButtonStatusMessage):
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
        elif isinstance(message, UpdateLedStatusMessage):
            for channel in list(range(1, self.number_of_channels() + 1)):
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
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "on"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, ClearLedMessage):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "off"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, SlowBlinkingLedMessage):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.leds:
                    self._led_state[channel] = "slow"
                if channel in self._led_state and channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._led_state[channel])
        elif isinstance(message, FastBlinkingLedMessage):
            for channel in list(range(1, self.number_of_channels() + 1)):
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
        if channel in self._is_enabled and self._is_enabled[channel]:
            return ["binary_sensor", "light"]
        else:
            return []


class VMB6PBNModule(VMB2PBNModule):
    """
    Velbus input module with 6 channels
    """

    def number_of_channels(self):
        return 6


class VMB8PBUModule(VMB2PBNModule):
    """
    Velbus input module with 8 channels
    """

    def number_of_channels(self):
        return 8


class VMB8PBModule(VMB2PBNModule):
    """
    Velbus input module with 8 channels
    """

    def __init__(self, module_type, module_name, module_address, controller):
        super().__init__(module_type, module_name, module_address, controller)
        for channel in list(range(1, self.number_of_channels() + 1)):
            self._is_enabled[channel] = True

    def number_of_channels(self):
        return 8


register_module("VMB2PBN", VMB2PBNModule)
register_module("VMB6PBN", VMB6PBNModule)
register_module("VMB8PBU", VMB8PBUModule)
register_module("VMB8PB", VMB8PBModule)
