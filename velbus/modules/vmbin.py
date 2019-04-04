"""
:author: Thomas Delaet <thomas@delaet.org
"""
import velbus


class VMB6INModule(velbus.Module):
    """
    Velbus input module with 6 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._callbacks = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def number_of_channels(self):
        return 6

    def _on_message(self, message):
        if isinstance(message, velbus.PushButtonStatusMessage):
            for channel in message.closed:
                self._is_closed[channel] = True
            for channel in message.opened:
                self._is_closed[channel] = False
            for channel in message.get_channels():
                if channel in self._callbacks:
                    for callback in self._callbacks[channel]:
                        callback(self._is_closed[channel])
        elif isinstance(message, velbus.ModuleStatusMessage):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.closed:
                    self._is_closed[channel] = True
                else:
                    self._is_closed[channel] = False

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        return ['binary_sensor']


class VMB7INModule(VMB6INModule):
    """
    Velbus input module with 7 channels
    """
    def __init__(self, module_type, module_name, module_address, controller):
        velbus.Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._pulses = {}
        self._counter = {}
        self._delay = {}
        self._is_counter = []
        self._unit = {}
        self._callbacks = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def _load(self):
        # request the counter statuis
        message = velbus.CounterStatusRequestMessage(self._address)
        self._controller.send(message)
        # get the unit for the counters
        message = velbus.ReadDataFromMemoryMessage(self._address)
        message.high_address = 0x03
        message.low_address = 0xfe
        self._controller.send(message)

    def number_of_channels(self):
        return 8

    def _on_message(self, message):
        if isinstance(message, velbus.PushButtonStatusMessage):
            for channel in message.closed:
                self._is_closed[channel] = True
            for channel in message.opened:
                self._is_closed[channel] = False
            for channel in message.get_channels():
                self._call_callback(channel)
        elif isinstance(message, velbus.ModuleStatusMessage2):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.closed:
                    self._is_closed[channel] = True
                else:
                    self._is_closed[channel] = False
        elif isinstance(message, velbus.CounterStatusMessage):
            self._pulses[message.channel] = message.pulses
            self._counter[message.channel] = message.counter
            self._delay[message.channel] = message.delay
            self._is_counter.append(message.channel)
            self._call_callback(message.channel)
        elif isinstance(message, velbus.MemoryDataMessage):
            for chan in range(1, 5):
                val = message.data >> ((chan - 1) * 2)
                inp = val & 0x03
                if inp == 0x01:
                    self._unit[chan] = 'l/h'
                elif inp == 0x02:
                    self._unit[chan] = 'm3/h'
                elif inp == 0x03:
                    self._unit[chan] = 'W'

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        if channel in self._is_counter:
            return ['sensor']
        else:
            return ['binary_sensor']

    def get_state(self, channel):
        """
        Ignore channel
        """
        val = None
        if channel not in self._unit:
            return val
        if self._unit[channel] == 'l/h':
            val = ((1000 * 3600) / (self._delay[channel] * self._pulses[channel]))
        elif self._unit[channel] == 'm3/h':
            val = ((1000 * 3600) / (self._delay[channel] * self._pulses[channel]))
        elif self._unit[channel] == 'W':
            val = ((1000 * 1000 * 3600) / (self._delay[channel] * self._pulses[channel]))
            if val < 55:
                val = 0
        return round(val, 2)

    def get_class(self, channel):
        """
        Ignore channel
        """
        return 'counter'

    def get_unit(self, channel):
        """
        Ignore channel
        """
        if channel in self._unit:
            return self._unit[channel]
        else:
            return None


velbus.register_module('VMB7IN', VMB7INModule)
velbus.register_module('VMB6IN', VMB6INModule)
