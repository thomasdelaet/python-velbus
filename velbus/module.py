"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import string
import struct
import re
from velbus.messages.read_data_from_memory import ReadDataFromMemoryMessage
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
        self._name = {}
        self._address = module_address
        self._master_address = 0xFF
        self._sub_address = {}
        self.sub_module = 0
        self.serial = 0
        self.memory_map_version = 0
        self.build_year = 0
        self.build_week = 0
        self._is_loading = False

        """
        _channel_data holds info per channel

        keys:
        - Type          => the channelType
        - Name          => the channel Name
        - NameParts
            - dict      => parts of the received channel name
            - True      => This channel is lmeParts"]oaded
            - False     => No channel data received (yet)
        """
        self._channel_data = {}

        self._loaded_callbacks = []
        self.loaded = False

        self._controller = controller
        self._controller.subscribe(self.on_message)

    def get_module_name(self):
        """
        Returns the module model name

        :return: str
        """
        if isinstance(self._name, str):
            return self._name
        return self._model_name

    def get_module_address(self):
        """
        Returns the module address

        :return: int
        """
        return self._address

    def get_module_addresses(self):
        """
        Returns the module addresses
        This will be the master and all subaddresses

        :return: list
        """
        return [self._address] + list(self._sub_address.values())

    def get_name(self, channel):
        """
        Get name for one of the channels

        :return: str
        """
        return self._channel_data[channel]["Name"]

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

    def get_addressChannel_from_channel(self, channel):
        """
        Get the address and channel

        :return: tuple(address, channel)
        """
        if len(self._sub_address) == 0:
            return int(channel)
        if int(channel) < 9:
            return self._address

    def on_message(self, message):
        """
        Process received message
        """
        # only if the message is send to this module handle it
        if message.address not in self.get_module_addresses():
            return
        # handle the messages
        if isinstance(message, ChannelNamePart1Message) or isinstance(
            message, ChannelNamePart1Message2
        ):
            self._process_channel_name_message(1, message)
        elif isinstance(message, ChannelNamePart2Message) or isinstance(
            message, ChannelNamePart2Message2
        ):
            self._process_channel_name_message(2, message)
        elif isinstance(message, ChannelNamePart3Message) or isinstance(
            message, ChannelNamePart3Message2
        ):
            self._process_channel_name_message(3, message)
        elif isinstance(message, MemoryDataMessage):
            self._process_memory_data_message(message)
        elif isinstance(message, ModuleTypeMessage):
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
        # did we already start the loading?
        # this is needed for the submodules,
        # as the submodule address maps to the main module
        # this method can be called multiple times
        if self._is_loading:
            return
        if callback:
            self._loaded_callbacks.append(callback)
        # start the loading
        self._is_loading = True
        # load the data from the protocol desciption
        self._data = self._controller._module_data["ModuleTypes"][
            "{:02X}".format(self._type)
        ]
        # load the module status
        self._request_module_status()
        # load default channels
        self._load_default_channels()
        # load the data from memory ( the stuff that we need)
        self._load_memory()
        # load the channel names
        self._request_channel_name()
        # load the module specific stuff
        self._load()

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

    def _handle_match(self, matchDict, data):
        mResult = {}
        bData = "{:08b}".format(int(data))
        for _num, matchD in matchDict.items():
            tmp = {}
            for match, res in matchD.items():
                if re.fullmatch(match[1:], bData):
                    res2 = res.copy()
                    res2["Data"] = int(data)
                    tmp.update(res2)
            mResult[_num] = tmp
        result = {}
        for res in mResult.values():
            if "Channel" in res:
                result[int(res["Channel"])] = {}
                if (
                    "SubName" in res
                    and "Value" in res
                    and res["Value"] != "PulsePerUnits"
                ):
                    result[int(res["Channel"])] = {res["SubName"]: res["Value"]}
                else:
                    # Very specifick for vmb7in
                    # a = bit 0 to 5 = 0 to 63
                    # b = a * 100
                    b = (data & 0x3F) * 100
                    # c = bit 6 + 7
                    #   00 = x1
                    #   01 = x2,5
                    #   10 = x0.05
                    #   11 = x0.01
                    # d = b * c
                    if data >> 5 == 3:
                        d = b * 0.01
                    elif data >> 5 == 2:
                        d = b * 0.05
                    elif data >> 5 == 1:
                        d = b * 2.5
                    else:
                        d = b
                    result[int(res["Channel"])] = {res["Value"]: d}
        return result

    def _process_memory_data_message(self, message):
        addr = "{high:02X}{low:02X}".format(
            high=message.high_address, low=message.low_address
        )
        try:
            mdata = self._data["Memory"]["1"]["Address"][addr]
            if "ModuleName" in mdata and isinstance(self._name, dict):
                # if self._name is a dict we are still loading
                # if its a string it was already complete
                if message.data == 0xFF:
                    # modulename is complete
                    self._name = "".join(str(x) for x in self._name.values())
                else:
                    char = mdata["ModuleName"].split(":")[0]
                    self._name[int(char)] = chr(message.data)
            elif "Match" in mdata:
                for chan, cData in self._handle_match(
                    mdata["Match"], message.data
                ).items():
                    data = cData.copy()
                    self._channel_data[chan].update(data)
        except KeyError:
            pass

    def _process_channel_name_message(self, part, message):
        channel = int(message.channel)
        # some modules need a remap of the channel number
        if (
            channel not in self._channel_data
            and "ChannelNumbers" in self._data
            and "Name" in self._data["ChannelNumbers"]
            and "Map" in self._data["ChannelNumbers"]["Name"]
            and "{:02X}".format(channel) in self._data["ChannelNumbers"]["Name"]["Map"]
        ):
            channel = int(
                self._data["ChannelNumbers"]["Name"]["Map"]["{:02X}".format(channel)]
            )
        # if the nameParts key is no started, build it
        if not isinstance(self._channel_data[channel]["NameParts"], dict):
            self._channel_data[channel]["NameParts"] = {}
        self._channel_data[channel]["NameParts"][part] = message.name
        # if we have all 3 parts, generate the name
        if all(part in self._channel_data[channel]["NameParts"] for part in [1, 2, 3]):
            self._generate_name(channel)

    def _process_module_type_message(self, message):
        self.serial = message.serial
        self.memory_map_version = int(message.memory_map_version)
        self.build_year = int(message.build_year)
        self.build_week = int(message.build_week)

    def _process_module_subtype_message(self, message):
        self.serial = message.serial

    def _generate_name(self, channel):
        name_parts = self._channel_data[channel]["NameParts"]
        name = name_parts[1] + name_parts[2] + name_parts[3]
        self._channel_data[channel]["Name"] = "".join(
            filter(lambda x: x in string.printable, name)
        )
        self._channel_data[channel]["NameParts"] = True
        self._name_messages_complete()

    def _name_messages_complete(self):
        """
        Check if all name messages have been received
        """
        if self.loaded:
            return
        for data in self._channel_data.values():
            if isinstance(data["NameParts"], dict) or not data["NameParts"]:
                return
        # set that  we finished the module loading
        self.loaded = True
        for callback in self._loaded_callbacks:
            callback()
        self._loaded_callbacks = []

    def _request_module_status(self):
        message = ModuleStatusRequestMessage(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def _request_channel_name(self):
        if "AllChannelStatus" in self._data:
            message = ChannelNameRequestMessage(self._address)
            message.channels = list(range(1, 9))
            self._controller.send(message)
        else:
            message = ChannelNameRequestMessage(self._address)
            message.channels = list(range(1, max(self._channel_data) + 1))
            self._controller.send(message)

    def _load_memory(self):
        if "Memory" not in self._data:
            return

        for _memoryKey, memoryPart in self._data["Memory"].items():
            if "Address" in memoryPart:
                for addrAddr in memoryPart["Address"].keys():
                    addr = struct.unpack(
                        ">BB", struct.pack(">h", int("0x" + addrAddr, 0))
                    )
                    message = ReadDataFromMemoryMessage(self._address)
                    message.high_address = addr[0]
                    message.low_address = addr[1]
                    self._controller.send(message)

    def _load_default_channels(self):
        if "Channels" not in self._data:
            return

        for chan, chanData in self._data["Channels"].items():
            self._channel_data[int(chan)] = {
                "Type": chanData["Type"],
                "Name": chanData["Name"],
                "NameParts": False,
            }
            if "Editable" not in chanData or chanData["Editable"] != "yes":
                self._channel_data[int(chan)]["NameParts"] = True
