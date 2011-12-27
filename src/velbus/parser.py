"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import binascii
import velbus

class ParserError(Exception):
	"""
	Error when invalid message is received
	"""
	pass

class VelbusParser(object):
	"""
	Transform Velbus message from wire format to Message object
	"""
		
	def __init__(self, controller):
		assert isinstance(controller, velbus.Controller)
		self.controller = controller
	
	def split_in_messages(self, data):
		"""
		@return: None
		"""
		assert isinstance(data, str)
		assert len(data) > 0
		if len(data) < velbus.MINIMUM_MESSAGE_SIZE:
			raise ParserError("Velbus messages are minimum 6 bytes, this one \
								is only " + str(len(data)))
		while len(data) > 0 and data[0] == chr(velbus.START_BYTE):
			size = ord(data[3]) & 0x0F
			message = data[0:velbus.MINIMUM_MESSAGE_SIZE+size]
			message_object = self.parse(message)
			self.controller.new_message(message_object)
			data = data[velbus.MINIMUM_MESSAGE_SIZE+size:]
		if len(data) > 0:
			print "first byte of incoming data is not start byte, ignoring inputs"
		
	def parse(self, data):
		"""
		@return: None
		"""
		#pylint: disable-msg=R0201
		assert isinstance(data, str)
		assert len(data) > 0
		assert len(data) >= velbus.MINIMUM_MESSAGE_SIZE
		assert ord(data[0]) == velbus.START_BYTE
		#print " ".join([binascii.hexlify(x) for x in data])
		if len(data) > velbus.MAXIMUM_MESSAGE_SIZE:
			raise ParserError("Velbus messages are maximum " + \
							str(velbus.MAXIMUM_MESSAGE_SIZE) + \
							" bytes, this one  is " + str(len(data)))
		if ord(data[-1]) != velbus.END_BYTE:
			raise ParserError("end byte not correct") 
		priority = ord(data[1])
		if priority != velbus.LOW_PRIORITY and priority != velbus.HIGH_PRIORITY:
			raise ParserError("unrecognized priority")
		address = ord(data[2])
		rtr = (ord(data[3]) & velbus.RTR == velbus.RTR)
		data_size = ord(data[3]) & 0x0F
		if data_size + velbus.MINIMUM_MESSAGE_SIZE != len(data):
			raise ParserError("length of data size does not match " + \
								"actual length of message")
		if not velbus.checksum(data[:-2]) == data[-2]:
			raise ParserError("packet has no valid checksum")
		if data_size >= 1:
			if velbus.CommandRegistry.has_key(ord(data[4])):
				message = velbus.CommandRegistry[ord(data[4])]()
				message.populate(priority, address, rtr, data[5:-2])
				return message
			else:
				print "received unrecognized command " + str(binascii.hexlify(data[4]))
		else:
			if rtr:
				message = velbus.ModuleTypeRequestMessage()
				message.populate(priority, address, rtr, "")
				return message
			else:
				raise ParserError("zero sized message received without rtr set")