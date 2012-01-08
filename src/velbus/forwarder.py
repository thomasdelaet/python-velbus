"""
@author: Thomas Delaet <thomas@delaet.org>
"""
#pylint: disable-msg=E1101,W0232,W0404
import velbus
import twisted.internet.protocol
import twisted.protocols.basic
import os
import binascii
import logging

class VelbusForwarderProtocol(twisted.protocols.basic.NetstringReceiver):
	"""
	Protocol for communication between serial controller and local cloudcontrol
	"""
	#pylint: disable-msg=C0103
	
	def stringReceived(self, string):
		"""
		@return: None
		"""
		assert isinstance(string, str)
		self.factory.stringReceived(string)
	
	def connectionMade(self):
		"""
		@return: None
		"""
		logging.info("connection made")
		self.factory.register(self)
	
	def connectionLost(self, reason=twisted.internet.protocol.connectionDone):
		"""
		@return: None
		"""
		logging.info("connection lost")
		self.factory.unregister(self)

class VelbusForwarderFactory(twisted.internet.protocol.Factory):
	"""
	Factory for communication between serial controller and local cloudcontrol
	"""	
	protocol = VelbusForwarderProtocol
	
	def __init__(self, velbus_service):
		assert isinstance(velbus_service, velbus.Controller)
		self.connections = []
		self.velbus_service = velbus_service
		self.velbus_service.subscribe(self.send)
		self.module_addresses = set()
		self.set_module_addresses()
		
	def stringReceived(self, string):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		assert isinstance(string, str)
		self.velbus_service.send_binary(string)
	
	def send(self, message):
		"""
		@return: None
		"""
		assert isinstance(message, velbus.Message)
		if not self.send_from_configured_module(message):
			return
		for connection in self.connections:
			connection.sendString(message.to_binary())
	
	def set_module_addresses(self):
		"""
		@return: None
		"""
		if os.environ.has_key('CONFIGURED_VELBUS_MODULES'):
			env = os.environ['CONFIGURED_VELBUS_MODULES'].split(" ")
		else:
			env = []
		for module_address in env:
			address = ord(binascii.unhexlify(module_address))
			self.module_addresses.add(address)		
	
	def send_from_configured_module(self, message):
		"""
		@return: bool
		"""
		assert isinstance(message, velbus.Message)
		if not len(self.module_addresses):
			return message.address in self.module_addresses
		else:
			return True
	
	def register(self, protocol):
		"""
		@return: None
		"""
		assert isinstance(protocol, VelbusForwarderProtocol)
		logging.debug("register connection")
		self.connections.append(protocol)
		
	def unregister(self, protocol):
		"""
		@return: None
		"""
		assert isinstance(protocol, VelbusForwarderProtocol)
		logging.debug("unregister connection")
		self.connections.remove(protocol)

class VelbusForwarder(object):
	"""
	Controller for communication between serial controller and local cloudcontrol
	"""
	#pylint: disable-msg=R0903
	
	def __init__(self, velbus_service, reactor):
		assert isinstance(velbus_service, velbus.Controller)
		reactor.listenTCP(8007, VelbusForwarderFactory(velbus_service))