"""
@author: Thomas Delaet <thomas@delaet.org>
"""
#pylint: disable-msg=E1101,W0232,W0404
import velbus
import twisted.protocols.basic
import twisted.internet.protocol

class NetstringProtocol(twisted.protocols.basic.NetstringReceiver):
	"""
	NetstringProtocol for communication between serial controller and local cloudcontrol
	"""
	def __init__(self, factory):
		self.factory = factory
	
	def stringReceived(self, string):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		assert isinstance(string, str)
		self.factory.stringReceived(string)

class VelbusClientFactory(twisted.internet.protocol.ReconnectingClientFactory):
	#pylint: disable-msg=C0103
	"""
	ClientFactory for communication between serial controller and local cloudcontrol
	"""
	
	def __init__(self, connection):
		assert isinstance(connection, velbus.VelbusConnection)
		self.connection = connection
		self.current_protocol = None
		self.maxDelay = 2
	
	def buildProtocol(self, addr):
		"""
		@return: NetstringProtocol
		"""
		self.resetDelay()
		self.current_protocol = NetstringProtocol(self)
		return self.current_protocol

	def stringReceived(self, string):
		"""
		@return: None
		"""
		assert isinstance(string, str)
		self.connection.stringReceived(string)

class NetstringConnection(velbus.VelbusConnection):
	"""
	Velbus connection for communication between serial controller and local cloudcontrol
	"""
	def __init__(self, host, port, reactor):
		velbus.VelbusConnection.__init__(self)
		assert isinstance(host, str)
		assert isinstance(port, int)
		self.factory = VelbusClientFactory(self)
		reactor.connectTCP(host, port, self.factory)
	
	def send(self, message):
		"""
		@return: None
		"""
		assert isinstance(message, velbus.Message)
		self.factory.current_protocol.sendString(message.to_binary())
		
	def stringReceived(self, string):
		"""
		@return: None
		"""
		#pylint: disable-msg=C0103
		assert isinstance(string, str)
		self.controller.split_in_messages(string)