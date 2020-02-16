"""
:author: Thomas Delaet <thomas@delaet.org
"""
from velbus.constants import (
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    VOLUME_CUBIC_METER,
    VOLUME_CUBIC_METER_HOUR,
    VOLUME_LITERS,
    VOLUME_LITERS_HOUR,
)
from velbus.module import Module
from velbus.module_registry import register_module
from velbus.messages.push_button_status import PushButtonStatusMessage
from velbus.messages.module_status import ModuleStatusMessage, ModuleStatusMessage2
from velbus.messages.counter_status import CounterStatusMessage
from velbus.messages.counter_status_request import CounterStatusRequestMessage
from velbus.messages.read_data_from_memory import ReadDataFromMemoryMessage
from velbus.messages.memory_data import MemoryDataMessage


class VMB6INModule(Module):
    """
    Velbus input module with 6 channels
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._callbacks = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def _call_callback(self, channel):
        if channel in self._callbacks:
            for callback in self._callbacks[channel]:
                callback(self._is_closed[channel])

    def number_of_channels(self):
        return 6

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
        elif isinstance(message, ModuleStatusMessage):
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
        return ["binary_sensor"]


class VMB7INModule(VMB6INModule):
    """
    Velbus input module with 7 channels
    """

    def __init__(self, module_type, module_name, module_address, controller):
        Module.__init__(self, module_type, module_name, module_address, controller)
        self._is_closed = {}
        self._is_enabled = {}
        self._pulses = {}
        self._counter = {}
        self._delay = {}
        self._is_counter = []
        self._unit = {}
        self._counter_unit = {}
        self._callbacks = {}

    def is_closed(self, channel):
        if channel in self._is_closed:
            return self._is_closed[channel]
        return False

    def _load(self):
        # request the counter status
        message = CounterStatusRequestMessage(self._address)
        self._controller.send(message)
        # get the unit for the counters
        message = ReadDataFromMemoryMessage(self._address)
        message.high_address = 0x03
        message.low_address = 0xFE
        self._controller.send(message)

    def number_of_channels(self):
        return 8

    def _on_message(self, message):
        if isinstance(message, PushButtonStatusMessage):
            for channel in message.closed:
                self._is_closed[channel] = True
            for channel in message.opened:
                self._is_closed[channel] = False
            for channel in message.get_channels():
                self._call_callback(channel)
        elif isinstance(message, ModuleStatusMessage2):
            for channel in list(range(1, self.number_of_channels() + 1)):
                if channel in message.closed:
                    self._is_closed[channel] = True
                else:
                    self._is_closed[channel] = False
        elif isinstance(message, CounterStatusMessage):
            self._pulses[message.channel] = message.pulses
            self._counter[message.channel] = message.counter
            self._delay[message.channel] = message.delay
            self._is_counter.append(message.channel)
            self._call_callback(message.channel)
        elif isinstance(message, MemoryDataMessage):
            for chan in range(1, 5):
                val = message.data >> ((chan - 1) * 2)
                inp = val & 0x03
                if inp == 0x01:
                    self._unit[chan] = VOLUME_LITERS_HOUR
                    self._counter_unit[chan] = VOLUME_LITERS
                elif inp == 0x02:
                    self._unit[chan] = VOLUME_CUBIC_METER_HOUR
                    self._counter_unit[chan] = VOLUME_CUBIC_METER
                elif inp == 0x03:
                    self._unit[chan] = ENERGY_WATT_HOUR
                    self._counter_unit[chan] = ENERGY_KILO_WATT_HOUR

    def on_status_update(self, channel, callback):
        """
        Callback to execute on status of update of channel
        """
        if channel not in self._callbacks:
            self._callbacks[channel] = []
        self._callbacks[channel].append(callback)

    def get_categories(self, channel):
        if channel in self._is_counter:
            return ["sensor"]
        else:
            return ["binary_sensor"]

    def get_counter_state(self, channel):
        if channel in self._counter:
            return self._counter[channel]
        return None

    def get_counter_unit(self, channel):
        if channel in self._counter_unit:
            return self._counter_unit[channel]
        return None

    def get_state(self, channel):
        val = 0
        # if we don't know the delay
        # or we don't know the unit
        # or the daly is the max value
        #   we always return 0
        if (
            channel not in self._delay
            or channel not in self._unit
            or self._delay[channel] == 0xFFFF
        ):
            return round(0, 2)
        if self._unit[channel] == VOLUME_LITERS_HOUR:
            val = (1000 * 3600) / (self._delay[channel] * self._pulses[channel])
        elif self._unit[channel] == VOLUME_CUBIC_METER_HOUR:
            val = (1000 * 3600) / (self._delay[channel] * self._pulses[channel])
        elif self._unit[channel] == ENERGY_WATT_HOUR:
            val = (1000 * 1000 * 3600) / (self._delay[channel] * self._pulses[channel])
        else:
            val = 0
        return round(val, 2)

    def get_class(self, channel):
        """
        Ignore channel
        """
        return "counter"

    def get_unit(self, channel):
        if channel in self._unit:
            return self._unit[channel]
        else:
            return None


register_module("VMB7IN", VMB7INModule)
register_module("VMB6IN", VMB6INModule)
