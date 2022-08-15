"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import string
import struct
from velbus.messages.read_data_from_memory import ReadDataFromMemoryMessage
from datetime import datetime, timedelta
from velbus.messages.memory_data import MemoryDataMessage
from velbus.messages.channel_name_part1 import ChannelNamePart1Message
from velbus.messages.channel_name_part1 import ChannelNamePart1Message2
from velbus.messages.channel_name_part2 import ChannelNamePart2Message
from velbus.messages.channel_name_part2 import ChannelNamePart2Message2
from velbus.messages.channel_name_part3 import ChannelNamePart3Message
from velbus.messages.channel_name_part3 import ChannelNamePart3Message2
from velbus.messages.module_type import ModuleTypeMessage
from velbus.messages.module_subtype import ModuleSubTypeMessage
from velbus.messages.module_status_request import ModuleStatusRequestMessage
from velbus.messages.channel_name_request import ChannelNameRequestMessage


class Module(object):
    """
    Abstract class for Velbus hardware modules.
    """

    def __init__(self, module_type, module_name, module_address, controller):
        self._type = module_type
        self._model_name = module_name
        self._name = False
        self._address = module_address
        self._master_address = 0xFF
        self.sub_module = 0
        self.serial = 0
        self.memory_map_version = 0
        self.build_year = 0
        self.build_week = 0

        self._channel_names = {}
        self._name_data = {}

        self._loaded_callbacks = []
        self.loaded = False
        self._loading_triggered = False

        self._last_channel_name_msg = datetime.utcnow()
        self._controller = controller
        self._controller.subscribe(self.on_message)

        if not self._is_submodule():
            self._data = controller._module_data["0x{:02x}".format(module_type)]
        else:
            self._data = {}
        self._memoryRead = {}

    def get_module_name(self):
        """
        Returns the module model name

        :return: str
        """
        if self._name:
            return self._name
        return self._model_name

    def get_module_address(self):
        """
        Returns the module address

        :return: int
        """
        return self._address

    def get_name(self, channel):
        """
        Get name for one of the channels

        :return: str
        """
        return self._channel_names[channel]

    def get_module_type_name(self):
        return self._model_name

    def get_type(self):
        return self._type

    def get_categories(self, channel):
        """
        Get type of functionality of channel

        :return: str
        """
        return []

    def on_message(self, message):
        """
        Process received message
        """
        if isinstance(message, ChannelNamePart1Message) or isinstance(
            message, ChannelNamePart1Message2
        ):
            if (message.address == self._address) or (
                self._is_submodule() and (message.address == self._master_address)
            ):
                self._process_channel_name_message(1, message)
        elif isinstance(message, ChannelNamePart2Message) or isinstance(
            message, ChannelNamePart2Message2
        ):
            if (message.address == self._address) or (
                self._is_submodule() and (message.address == self._master_address)
            ):
                self._process_channel_name_message(2, message)
        elif isinstance(message, ChannelNamePart3Message) or isinstance(
            message, ChannelNamePart3Message2
        ):
            if (message.address == self._address) or (
                self._is_submodule() and (message.address == self._master_address)
            ):
                self._process_channel_name_message(3, message)
        elif isinstance(message, MemoryDataMessage):
            if message.address == self._address:
                for typ, item in self._memoryRead.items():
                    if (message.high_address, message.low_address) in item:
                        if message.data == 0xFF:
                            self._memoryRead[typ].remove(
                                (message.high_address, message.low_address)
                            )
                            if typ == "moduleName":
                                self._moduleName_is_complete()
                        else:
                            idx = [
                                i
                                for i, x in enumerate(self._memoryRead[typ])
                                if x == (message.high_address, message.low_address)
                            ]
                            self._memoryRead[typ][idx[0]] = chr(message.data)
                        break
        else:
            if message.address == self._address:
                if isinstance(message, ModuleTypeMessage):
                    self._process_module_type_message(message)
                elif isinstance(message, ModuleSubTypeMessage):
                    self._process_module_subtype_message(message)
                else:
                    self._on_message(message)

    def _on_message(self, message):
        pass

    def load(self, callback):
        """
        Retrieve names of channels
        """
        if not self.loaded:
            if not self._loading_triggered:
                self._loading_triggered = True
                if not self._is_submodule():
                    # load the data from memory ( the stuff that we need)
                    self._load_memory()
                # load the module status
                self._request_module_status()
                if not self._is_submodule():
                    # load the channel names
                    self._request_channel_name()
                # load the module specific stuff
                self._load()
            else:
                # Request channel names if last received
                if (
                    not self._is_submodule()
                    and not self._name_messages_complete()
                    and self._last_channel_name_msg
                    < datetime.utcnow() - timedelta(seconds=10)
                ):
                    self._request_channel_name()
            if callback:
                self._loaded_callbacks.append(callback)
        else:
            if callback:
                callback()

    def loading_in_progress(self):
        return not self._name_messages_complete()

    def _load(self):
        pass

    def number_of_channels(self):
        """
        Retrieve the number of available channels in this module

        :return: int
        """
        raise NotImplementedError

    def light_is_buttonled(self, channel):
        return False

    def _is_submodule(self):
        return False

    def _name_count_needed(self):
        return self.number_of_channels() * 3

    def _process_channel_name_message(self, part, message):
        self._last_channel_name_msg = datetime.utcnow()
        channel = message.channel
        if self._is_submodule():
            channel = channel - (self.number_of_channels() * self.sub_module)
            if 1 <= channel <= self.number_of_channels():
                if channel not in self._name_data:
                    self._name_data[channel] = {}
                self._name_data[channel][part] = message.name
                if self._name_messages_complete():
                    self._generate_names()
        else:
            if channel <= self.number_of_channels():
                if channel not in self._name_data:
                    self._name_data[channel] = {}
                self._name_data[channel][part] = message.name
                if self._name_messages_complete():
                    self._generate_names()

    def _process_module_type_message(self, message):
        self.serial = message.serial
        self.memory_map_version = int(message.memory_map_version)
        self.build_year = int(message.build_year)
        self.build_week = int(message.build_week)

    def _process_module_subtype_message(self, message):
        self.serial = message.serial

    def _generate_names(self):
        assert self._name_messages_complete()
        for channel in range(1, self.number_of_channels() + 1):
            name_parts = self._name_data[channel]
            name = name_parts[1] + name_parts[2] + name_parts[3]
            self._channel_names[channel] = "".join(
                filter(lambda x: x in string.printable, name)
            )
        self._name_data = {}
        self.loaded = True
        for callback in self._loaded_callbacks:
            callback()
        self._loaded_callbacks = []

    def _name_messages_complete(self):
        """
        Check if all name messages have been received
        """
        for channel in range(1, self.number_of_channels() + 1):
            try:
                for name_index in range(1, 4):
                    if not isinstance(self._name_data[channel][name_index], str):
                        return False
            except KeyError:
                return False
        return True

    def _moduleName_is_complete(self):
        self._name = ""
        for char in self._memoryRead["moduleName"]:
            if type(char) is str:
                self._name = self._name + char
        del self._memoryRead["moduleName"]

    def _request_module_status(self):
        message = ModuleStatusRequestMessage(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def _request_channel_name(self):
        message = ChannelNameRequestMessage(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def _load_memory(self):
        if "memory" not in self._data:
            return

        for memoryType, matchData in self._data["memory"].items():
            self._memoryRead[memoryType] = []
            # TODO matchbuild + matchversion
            for addrRange in matchData["address"].split(";"):
                addrR = addrRange.split("-")
                for addr in range(int(addrR[0], 0), int(addrR[1], 0)):
                    addr = struct.unpack(">BB", struct.pack(">h", addr))
                    self._memoryRead[memoryType].append(addr)
                    message = ReadDataFromMemoryMessage(self._address)
                    message.high_address = addr[0]
                    message.low_address = addr[1]
                    self._controller.send(message)
