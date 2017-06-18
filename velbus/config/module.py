"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbusconfig


class VelbusModule(object):
    """
    Base Velbus channel
    """

    def __init__(self, controller, address, channel):
        assert isinstance(controller, velbusconfig.Controller)
        assert velbusconfig.valid_key(address, channel)
        self.controller = controller
        self.address = address
        self.channel = channel
        self.is_on = False

    def to_string(self):
        raise NotImplementedError

    def key(self):
        """
        @return: tuple(int, int)
        """
        return (self.address, self.channel)

    def set_on(self):
        """
        @return: None
        """
        self.is_on = True

    def set_off(self):
        """
        @return: None
        """
        self.is_on = False
