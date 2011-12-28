"""
@author: Thomas Delaet <thomas@delaet.org>
"""
from twisted.internet.protocol import Protocol, connectionDone
import logging
import velbus
import binascii

class VelbusProtocol(Protocol):
	"""
	Velbus protocol adapter
	"""

	def __init__(self, connection):
		assert isinstance(connection, velbus.VelbusUSBConnection)
		self.connection = connection

	def dataReceived(self, data):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		assert isinstance(data, str)
		logging.debug("Data Received: %s", " ".join([binascii.hexlify(x) for x in data]))
		self.connection.split_in_messages(data)
	
	def connectionLost(self, reason=connectionDone):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		logging.debug("Connection Lost %s", reason)

	def connectionMade(self):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		logging.debug("Connection made!")
		
	def write(self, data):
		"""
		@return: None
		"""
		assert isinstance(data, str)
		self.transport.write(data)