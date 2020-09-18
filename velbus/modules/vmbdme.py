"""
:author: Frank van Breugel
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.set_dimmer import SetDimmerMessage
from velbus.messages.restore_dimmer import RestoreDimmerMessage
from velbus.messages.dimmer_status import DimmerStatusMessage
from velbus.messages.slider_status import SliderStatusMessage


class VMBDMEModule(Module):
    """
    Velbus dimmer module with 1 channel
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._dimmer_state = {}
        self._callbacks = {}

    def number_of_channels(self):
        return 1

    def is_on(self, channel):
        """
        Check if a dimmer is turned on

        :return: bool
        """
        if channel in self._dimmer_state:
            if self._dimmer_state[channel] == 0:
                return False
            else:
                return True
        return False

    def get_dimmer_state(self, channel):
        """
        Return the dimmer state

        :return: int
        """
        if channel in self._dimmer_state:
            return self._dimmer_state[channel]
        return 0

    def set_dimmer_state(self, channel, slider, transitiontime=0, callback=None):
        """
        Set dimmer to slider

        :return: None
        """
        if callback is None:

            def callb():
                """No-op"""
                pass

            callback = callb
        message = SetDimmerMessage(self._address)
        message.dimmer_channels = [channel]
        message.dimmer_state = slider
        message.dimmer_transitiontime = int(transitiontime)
        self._controller.send(message, callback)

    def restore_dimmer_state(self, channel, transitiontime=0, callback=None):
        """
        restore dimmer to last known state

        :return: None
        """
        if callback is None:

            def callb():
                """No-op"""
                pass

            callback = callb
        message = RestoreDimmerMessage(self._address)
        message.dimmer_channels = [channel]
        message.dimmer_transitiontime = int(transitiontime)
        self._controller.send(message, callback)

    def _on_message(self, message):
        if isinstance(message, DimmerStatusMessage):
            self._dimmer_state[message.channel] = message.cur_dimmer_state()
            if message.channel in self._callbacks:
                for callback in self._callbacks[message.channel]:
                    callback(message.cur_dimmer_state())
        if isinstance(message, SliderStatusMessage):
            self._dimmer_state[message.channel] = message.cur_slider_state()
            if message.channel in self._callbacks:
                for callback in self._callbacks[message.channel]:
                    callback(message.cur_slider_state())

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        return ["light"]

    def light_is_buttonled(self, channel):
        return False


register_module("VMBDME", VMBDMEModule)
register_module("VMB1LED", VMBDMEModule)
