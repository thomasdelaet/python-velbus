"""
@author: Thomas Delaet <thomas@delaet.org>
"""
MINIMUM_MESSAGE_SIZE = 6

MAXIMUM_MESSAGE_SIZE = MINIMUM_MESSAGE_SIZE + 8

START_BYTE = 0x0f

END_BYTE = 0x04

LOW_PRIORITY = 0xfb

HIGH_PRIORITY = 0xf8

LOW_ADDRESS = 0x00

HIGH_ADDRESS = 0xff

RTR = 0x40

NO_RTR = 0x00

SIX_CHANNEL_INPUT_MODULE_TYPE = 0x05

VMB4RYLD_TYPE = 0x10

#pylint: disable-msg=C0103
CommandRegistry = {}

import os

def on_app_engine():
	"""
	@return: bool
	"""
	if os.environ.has_key('SERVER_SOFTWARE'):
		server_software = os.environ['SERVER_SOFTWARE']
		if server_software.startswith('Google App Engine') or \
			server_software.startswith('Development'):
			return True
		else:
			return False
	else:
		return False

def register_command(command_value, command_class):
	"""
	@return: None
	"""
	assert isinstance(command_value, int)
	assert command_value >= 0 and command_value <= 255
	assert isinstance(command_class, type)
	if not CommandRegistry.has_key(command_value):
		CommandRegistry[command_value] = command_class
	else:
		raise Exception("double registration in command registry")   

def checksum(data):
	"""
	@return: str(1)
	"""
	assert isinstance(data, str)
	assert len(data) >= MINIMUM_MESSAGE_SIZE - 2
	assert len(data) <= MAXIMUM_MESSAGE_SIZE - 2
	__checksum = 0
	for data_byte in data:
		__checksum += ord(data_byte)
	__checksum = -(__checksum % 256) + 256
	return chr(__checksum)

#pylint: disable-msg=W0401
from message import Message
from messages import *

from parser import VelbusParser, ParserError

from controller import Controller, VelbusConnection

if not on_app_engine():
	try:
		from connections.usb import VelbusUSBConnection
	except ImportError:
		pass
	from connections.netstring import NetstringConnection
	from forwarder import VelbusForwarder