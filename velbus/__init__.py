"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import os

MINIMUM_MESSAGE_SIZE = 6

MAXIMUM_MESSAGE_SIZE = MINIMUM_MESSAGE_SIZE + 8

START_BYTE = 0x0f

END_BYTE = 0x04

HIGH_PRIORITY = 0xf8
FIRMWARE_PRIORITY = 0xf9
THIRD_PARTY_PRIORITY = 0xfa
LOW_PRIORITY = 0xfb
PRIORITY = [HIGH_PRIORITY, FIRMWARE_PRIORITY, THIRD_PARTY_PRIORITY, LOW_PRIORITY] 

LOW_ADDRESS = 0x00

HIGH_ADDRESS = 0xff

RTR = 0x40

NO_RTR = 0x00

SIX_CHANNEL_INPUT_MODULE_TYPE = 0x05

MODULE_DIRECTORY = {
    0x01: 'VMB8PB',
    0x02: 'VMB1RY',
    0x03: 'VMB1BL',
    0x05: 'VMB6IN',
    0x07: 'VMB1DM',
    0x08: 'VMB4RY',
    0x09: 'VMB2BL',
    0x0a: 'VMB8IR',
    0x0b: 'VMB4PD',
    0x0c: 'VMB1TS',
    0x0d: 'VMB1TH',
    0x0e: 'VMB1TC',
    0x0f: 'VMB1LED',
    0x10: 'VMB4RYLD',
    0x11: 'VMB4RYNO',
    0x12: 'VMB4DC',
    0x13: 'VMBLCDWB',
    0x14: 'VMBDME',
    0x15: 'VMBDMI',
    0x16: 'VMB8PBU',
    0x17: 'VMB6PBN',
    0x18: 'VMB2PBN',
    0x19: 'VMB6PBB',
    0x1a: 'VMB4RF',
    0x1b: 'VMB1RYNO',
    0x1c: 'VMB1BLE',
    0x1d: 'VMB2BLE',
    0x1e: 'VMBGP1',
    0x1f: 'VMBGP2',
    0x20: 'VMBGP4',
    0x21: 'VMBGP0',
    0x22: 'VMB7IN',
    0x28: 'VMBGPOD',
    0x29: 'VMB1RYNOS',
    0x2a: 'VMBIRM',
    0x2b: 'VMBIRC',
    0x2c: 'VMBIRO',
    0x2d: 'VMBGP4PIR',
    0x2e: 'VMB1BLS',
    0x2f: 'VMBDMI-R',
    0x31: 'VMBMETEO',
    0x32: 'VMB4AN',
    0x33: 'VMBVP01',
    0x34: 'VMBEL1',
    0x35: 'VMBEL2',
    0x36: 'VMBEL4',
    0x37: 'VMBELO',
    0x39: 'VMBSIG',
    0x3A: 'VMBGP1-2',
    0x3B: 'VMBGP2-2',
    0x3C: 'VMBGP4-2',
    0x3D: 'VMBGPOD-2',
    0x3E: 'VMBGP4PIR-2'
}

#pylint: disable-msg=C0413
from velbus.command_registry import CommandRegistry
commandRegistry = CommandRegistry(MODULE_DIRECTORY)

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


def register_command(command_value, command_class, module_type=0):
    """
    :return: None
    """
    commandRegistry.register_command(command_value, command_class, module_type)


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
