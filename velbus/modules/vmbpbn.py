"""
:author: Thomas Delaet <thomas@delaet.org
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.push_button_status import PushButtonStatusMessage
from velbus.messages.module_status import ModuleStatusMessage2


class VMB2PBNModule(Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._callbacks = {}

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

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        if channel in self._is_enabled and self._is_enabled[channel]:
            return ['binary_sensor']
        else:
            return []


class VMB6PBNModule(VMB2PBNModule):
    """
    Velbus input module with 7 channels
    """
    def number_of_channels(self):
        return 6


class VMB8PBUModule(VMB2PBNModule):
    """
    Velbus input module with 7 channels
    """
    def number_of_channels(self):
        return 6


register_module('VMB2PBN', VMB2PBNModule)
register_module('VMB6PBN', VMB6PBNModule)
register_module('VMB8PBU', VMB8PBUModule)
