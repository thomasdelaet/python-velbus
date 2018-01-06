"""
@author: Thomas Delaet <thomas@delaet.org>
"""
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
        self._name_callback = None
        self._controller = controller
        self._name_count_received = 0
        self._name_count_data = {}
        self.loaded = False
        self._controller.subscribe(self.on_message)

    def get_module_name(self):
        """
        Returns the module model name

        @return: str
        """
        return self._name

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

    def load(self):
        """
        Retrieve names of channels
        """
        self._name_count_received = 0
        message = velbus.ChannelNameRequestMessage(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def number_of_channels(self):
        """
        Retrieve the number of avaiable channels in this module

        @return: int
        """
        raise NotImplementedError

    def _name_count_needed(self):
        return self.number_of_channels() * 3

    def _process_channel_name_message(self, part, message):
        self._name_count_received += 1
        channel = message.channel
        if channel not in self._name_count_data:
            self._name_count_data[channel] = {}
        self._name_count_data[channel][part] = message.name
        if self._name_count_needed() <= self._name_count_received:
            self._generate_names()

    def _generate_names(self):
        for channel in range(1, self.number_of_channels() + 1):
            name_parts = self._name_count_data[channel]
            name = name_parts[1] + name_parts[2] + name_parts[3]
            self._channel_names[channel] = name.rstrip('\xff')
        self._name_callback = None
        self._name_count_received = 0
        self._name_count_data = {}
        self.loaded = True
