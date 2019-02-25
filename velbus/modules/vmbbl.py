"""
:author: Maikel Punie <maikel.punie@gmail.com>
"""
import velbus


class VMB1BLModule(velbus.Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
        self._state = {}
        self._callbacks = {}

    def number_of_channels(self):
        return 1

    def _on_message(self, message):
        if isinstance(message, velbus.BlindStatusNgMessage):
            self._state[message.channel] = message.blind_position
            self._call_callback(message.channel)
        if isinstance(message, velbus.BlindStatusMessage):
            self._state[message.channel] = message.blind_position
            self._call_callback(message.channel)

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
        message = velbus.ChannelNameRequestMessage2(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def open(self, channel):
        message = velbus.CoverUpMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def close(self, channel):
        message = velbus.CoverDownMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def stop(self, channel):
        message = velbus.CoverOffMessage2(self._address)
        message.channel = channel
        self._controller.send(message)

    def get_state(self, channel):
        if channel not in self._state:
            return None
        return self._state[channel]

    def _call_callback(self, channel):
        if channel in self._callbacks:
            for callback in self._callbacks[channel]:
                callback(self._state[channel])


class VMB2BLModule(VMB1BLModule):
    def number_of_channels(self):
        return 2


class VMB1BLEModule(VMB1BLModule):
    def number_of_channels(self):
        return 1

    def open(self, channel):
        message = velbus.CoverUpMessage(self._address)
        message.channel = channel
        self._controller.send(message)

    def close(self, channel):
        message = velbus.CoverDownMessage(self._address)
        message.channel = channel
        self._controller.send(message)

    def stop(self, channel):
        message = velbus.CoverOffMessage(self._address)
        message.channel = channel
        self._controller.send(message)


class VMB2BLEModule(VMB1BLEModule):
    def number_of_channels(self):
        return 2


velbus.register_module('VMB1BL', VMB1BLModule)
velbus.register_module('VMB2BL', VMB2BLModule)
velbus.register_module('VMB1BLE', VMB1BLEModule)
velbus.register_module('VMB2BLE', VMB2BLEModule)
