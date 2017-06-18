"""
@author: Thomas Delaet <thomas@delaet.org>
"""
from velbusconfig.module import VelbusModule
from relay import Relay
from switch import Switch
from switch_config_reader import SwitchConfigReader
from controller import Controller

LOW_ADDRESS = 0x00

HIGH_ADDRESS = 0xff


def valid_key(address, channel):
    """
    @return: bool
    """
    return isinstance(address, int) and \
        isinstance(channel, int) and \
        channel > 0 and \
        address >= LOW_ADDRESS and \
        address <= HIGH_ADDRESS
