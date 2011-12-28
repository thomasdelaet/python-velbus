"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import binascii

class VelbusConnection(object):
	#pylint: disable-msg=R0921
	"""
	Generic Velbus connection
	"""
	
	controller = None
		
	def set_controller(self, controller):
		"""
		@return: None
		"""
		assert isinstance(controller, Controller)
		self.controller = controller
		
	def send(self, message):
		"""
		@return: None
		"""
		raise NotImplementedError

class Controller(object):
	"""
	Velbus Bus connection controller
	"""
	
	def __init__(self, connection):
		self.connection = connection
		self.parser = velbus.VelbusParser(self)
		self.__subscribers = []
		self.connection.set_controller(self)
		
	def split_in_messages(self, data):
		"""
		@return: None
		"""
		assert isinstance(data, str)
		try:
			self.parser.split_in_messages(data)
		except velbus.ParserError, exception:
			print str(exception)
		
	def subscribe(self, subscriber):
		"""
		@return: None
		"""
		self.__subscribers.append(subscriber)
	
	def unsubscribe(self, subscriber):
		"""
		@return: None
		"""
		self.__subscribers.remove(subscriber)
	
	def send(self, message):
		"""
		@return: None
		"""
		self.connection.send(message)
		
	def send_binary(self, binary_message):
		"""
		@return: None
		"""
		assert isinstance(binary_message, str)
		message = self.parser.parse(binary_message)
		self.send(message)	
		
	def new_message(self, message):
		"""
		@return: None
		"""
		for subscriber in self.__subscribers:
			subscriber(message)