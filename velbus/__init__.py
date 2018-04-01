"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import os

MINIMUM_MESSAGE_SIZE = 6

MAXIMUM_MESSAGE_SIZE = MINIMUM_MESSAGE_SIZE + 8

START_BYTE = 0x0f

END_BYTE = 0x04

LOW_PRIORITY = 0xfb

HIGH_PRIORITY = 0xf8

FIRMWARE_PRIORITY = 0xf7

LOW_ADDRESS = 0x00

HIGH_ADDRESS = 0xff

RTR = 0x40

NO_RTR = 0x00

SIX_CHANNEL_INPUT_MODULE_TYPE = 0x05

VMB4RYLD_TYPE = 0x10

# pylint: disable-msg=C0103
CommandRegistry = {}

ModuleRegistry = {}

def on_app_engine():
    """
    :return: bool
    """
    if 'SERVER_SOFTWARE' in os.environ:
        server_software = os.environ['SERVER_SOFTWARE']
        if server_software.startswith('Google App Engine') or \
                server_software.startswith('Development'):
            return True
        return False
    return False


def register_command(command_value, command_class):
    """
    :return: None
    """
    assert isinstance(command_value, int)
    assert command_value >= 0 and command_value <= 255
    assert isinstance(command_class, type)
    if command_value not in CommandRegistry:
        CommandRegistry[command_value] = command_class
    else:
        raise Exception("double registration in command registry")

def register_module(module_name, module_class):
    """
    :return: None
    """
    assert isinstance(module_name, str)
    assert isinstance(module_class, type)
    if module_name not in ModuleRegistry:
        ModuleRegistry[module_name] = module_class
    else:
        raise Exception("double registration in module registry")

def checksum(data):
    """
    :return: int
    """
    assert isinstance(data, bytes)
    assert len(data) >= MINIMUM_MESSAGE_SIZE - 2
    assert len(data) <= MAXIMUM_MESSAGE_SIZE - 2
    __checksum = 0
    for data_byte in data:
        __checksum += data_byte
    __checksum = -(__checksum % 256) + 256
    try:
        __checksum = bytes([__checksum])
    except ValueError:
        __checksum = bytes([0])
    return __checksum

# pylint: disable-msg=W0401,C0413
from velbus.message import Message
from velbus.messages import *

from velbus.module import Module
from velbus.modules import *

from velbus.parser import VelbusParser, ParserError

from velbus.controller import Controller, VelbusConnection

if not on_app_engine():
    try:
        from velbus.connections import VelbusUSBConnection, VelbusSocketConnection
    except ImportError:
        pass
