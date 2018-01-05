"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

class Module(object):
    """
    Abstract class for Velbus hardware modules.
    """
    def __init__(self, module_type, module_name, module_address, controller):
        self._type = module_type
        self._name = module_name
        self._address = module_address
        self._channel_names = []
        self._name_callback = None
        self._controller = controller

    def get_name(self, callback=None):
        """
        Retrieve names of channels
        """
        self._name_callback = callback
        message = velbus.ChannelNameRequestMessage(self._address)
        message.channels = list(range(1, self.number_of_channels() + 1))
        self._controller.send(message)

    def number_of_channels(self):
        """
        Retrieve the number of avaiable channels in this module

        @return: int
        """
        raise NotImplementedError
