"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import string
import velbus

class Module(object):
    """
    Abstract class for Velbus hardware modules.
    """
    #pylint: disable-msg=R0902
    def __init__(self, module_type, module_name, module_address, controller):
        self._type = module_type
        self._name = module_name
        self._address = module_address

        self._channel_names = {}
        self._name_data = {}

        self._loaded_callbacks = []
        self.loaded = False

        self._controller = controller
        self._controller.subscribe(self.on_message)

    def get_module_name(self):
        """
        Returns the module model name

        :return: str
        """
        return self._name

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
        if message.address != self._address:
            return
        if isinstance(message, velbus.ChannelNamePart1Message):
            self._process_channel_name_message(1, message)
        elif isinstance(message, velbus.ChannelNamePart2Message):
            self._process_channel_name_message(2, message)
        elif isinstance(message, velbus.ChannelNamePart3Message):
            self._process_channel_name_message(3, message)
        else:
            self._on_message(message)

    def _on_message(self, message):
        pass

    def load(self, callback):
        """
        Retrieve names of channels
        """
        if callback is None:
            def callb():
                """No-op"""
                pass
            callback = callb
        if len(self._loaded_callbacks) == 0:
            message = velbus.ChannelNameRequestMessage(self._address)
            message.channels = list(range(1, self.number_of_channels() + 1))
            self._controller.send(message)
        self._loaded_callbacks.append(callback)
        self._load()

    def _load(self):
        pass

    def number_of_channels(self):
        """
        Retrieve the number of avaiable channels in this module

        :return: int
        """
        raise NotImplementedError

    def _name_count_needed(self):
        return self.number_of_channels() * 3

    def _process_channel_name_message(self, part, message):
        channel = message.channel
        if channel not in self._name_data:
            self._name_data[channel] = {}
        self._name_data[channel][part] = message.name
        if self._name_messages_complete():
            self._generate_names()

    def _generate_names(self):
        assert self._name_messages_complete()
        for channel in range(1, self.number_of_channels() + 1):
            name_parts = self._name_data[channel]
            name = name_parts[1] + name_parts[2] + name_parts[3]
            self._channel_names[channel] = ''.join(filter(lambda x: x in string.printable, name))
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
            except Exception:
                return False
        return True
