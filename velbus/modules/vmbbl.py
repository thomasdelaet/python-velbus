"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.cover_down import CoverDownMessage, CoverDownMessage2
from velbus.messages.cover_off import CoverOffMessage, CoverOffMessage2
from velbus.messages.cover_up import CoverUpMessage, CoverUpMessage2
from velbus.messages.blind_status import BlindStatusMessage, BlindStatusNgMessage
from velbus.messages.channel_name_request import ChannelNameRequestMessage2

class VMB1BLModule(Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._state = {}
        self._callbacks = {}

    def number_of_channels(self):
        return 1

    def _on_message(self, message):
        if isinstance(message, BlindStatusNgMessage):
            self._state[message.channel] = message.status
            if message.channel in self._callbacks:
                for callback in self._callbacks[message.channel]:
                    callback(message.is_down())
        if isinstance(message, BlindStatusMessage):
            self._state[message.channel] = message.status
            if message.channel in self._callbacks:
                for callback in self._callbacks[message.channel]:
                    callback(message.is_down())

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        return ['cover']

    def _request_channel_name(self):
        message = ChannelNameRequestMessage2(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def open(self, channel):
        message = CoverUpMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def close(self, channel):
        message = CoverDownMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def stop(self, channel):
        message = CoverOffMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def get_state(self, channel):
        if channel not in self._state:
            return None
        return self._state[channel]

    def is_closed(self, channel):
        if self.get_state(channel) == 0x02:
            return True
        return False

    def is_open(self, channel):
        if self.get_state(channel) == 0x01:
            return True
        return False


class VMB2BLModule(VMB1BLModule):
    def number_of_channels(self):
        return 2


class VMB1BLEModule(VMB1BLModule):
    def number_of_channels(self):
        return 1

    def open(self, channel):
        message = CoverUpMessage(self._address)
        message.channel = channel
        self._controller.send(message)

    def close(self, channel):
        message = CoverDownMessage(self._address)
        message.channel = channel
        self._controller.send(message)

    def stop(self, channel):
        message = CoverOffMessage(self._address)
        message.channel = channel
        self._controller.send(message)


class VMB2BLEModule(VMB1BLEModule):
    def number_of_channels(self):
        return 2


register_module('VMB1BL', VMB1BLModule)
register_module('VMB2BL', VMB2BLModule)
register_module('VMB1BLE', VMB1BLEModule)
register_module('VMB2BLE', VMB2BLEModule)
