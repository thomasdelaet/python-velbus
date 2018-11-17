"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

class VMB4RYModule(velbus.Module):
    """
    Velbus Relay module.
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_on = {}
        self._callbacks = {}

    def number_of_channels(self):
        return 5

    def is_on(self, channel):
        """
        Check if a switch is turned on

        :return: bool
        """
        if channel in self._is_on:
            return self._is_on[channel]
        return False

    def turn_on(self, channel, callback = None):
        """
        Turn on switch.

        :return: None
        """
        if callback is None:
            def callb():
                """No-op"""
                pass
            callback = callb
        message = velbus.SwitchRelayOnMessage(self._address)
        message.relay_channels = [channel]
        self._controller.send(message, callback)

    def turn_off(self, channel, callback=None):
        """
        Turn off switch.

        :return: None
        """
        if callback is None:
            def callb():
                """No-op"""
                pass
            callback = callb
        message = velbus.SwitchRelayOffMessage(self._address)
        message.relay_channels = [channel]
        self._controller.send(message, callback)

    def _on_message(self, message):
        if isinstance(message, velbus.RelayStatusMessage):
            self._is_on[message.channel] = message.is_on()
            if message.channel in self._callbacks:
                for callback in self._callbacks[message.channel]:
                    callback(message.is_on())

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if not channel in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        return ['switch']


velbus.register_module('VMB4RYLD', VMB4RYModule)
velbus.register_module('VMB4RYNO', VMB4RYModule)
velbus.register_module('VMB1RYNO', VMB4RYModule)
velbus.register_module('VMB1RYNOS', VMB4RYModule)
