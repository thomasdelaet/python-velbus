"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import binascii
import velbus
import threading

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
		self.buffer = ''
		self.event = threading.Event()
	
	def feed(self, data):
		self.buffer += data
		self.next_packet()

	def valid_header_waiting(self):
		if len(self.buffer) < 4:
			velbus.logger.debug("Buffer does not yet contain full header")
			result = False
		else:
			result = True
			result = result and self.buffer[0] == chr(velbus.START_BYTE)
			if not result:
				velbus.logger.warning("Start byte not recognized")
			result = result and (self.buffer[1] == chr(velbus.HIGH_PRIORITY) or self.buffer[1] == chr(velbus.LOW_PRIORITY)) 
			if not result:
				velbus.logger.warning("Priority not recognized")
			result = result and (ord(self.buffer[3]) & 0x0F <= 8)
			if not result:
				velbus.logger.warning("Message size not recognized")
		velbus.logger.debug("Valid Header Waiting: %s(%s)", result, " ".join([binascii.hexlify(x) for x in self.buffer]))
		return result
	
	def valid_body_waiting(self):
		#0f f8 be 04 00 08 00 00 2f 04
		packet_size = velbus.MINIMUM_MESSAGE_SIZE + (ord(self.buffer[3]) & 0x0F)
		if len(self.buffer) < packet_size:
			velbus.logger.debug("Buffer does not yet contain full message")
			result = False
		else:
			result = True
			result = result and ord(self.buffer[packet_size-1]) == velbus.END_BYTE
			if not result:
				velbus.logger.warning("End byte not recognized")
			result = result and velbus.checksum(self.buffer[0:packet_size-2]) == self.buffer[packet_size-2]
			if not result:
				velbus.logger.warning("Checksum not recognized")
		velbus.logger.debug("Valid Body Waiting: %s (%s)", result, " ".join([binascii.hexlify(x) for x in self.buffer]))
		return result
	
	def next_packet(self):
		try:
			start_byte_index = self.buffer.index(chr(velbus.START_BYTE))
		except ValueError:
			self.buffer = ''
			return
		if start_byte_index >= 0:
			self.buffer = self.buffer[start_byte_index:]
		if self.valid_header_waiting() and self.valid_body_waiting():
			next_packet = self.extract_packet()
			self.buffer = self.buffer[len(next_packet):]
			message = self.parse(next_packet)
			if isinstance(message, velbus.Message):
				self.controller.new_message(message)
	
	def extract_packet(self):
		packet_size = velbus.MINIMUM_MESSAGE_SIZE + (ord(self.buffer[3]) & 0x0F)
		packet = self.buffer[0:packet_size]
		return packet
	
	def parse(self, data):
		"""
		@return: None
		"""
		#pylint: disable-msg=R0201
		assert isinstance(data, str)
		assert len(data) > 0
		assert len(data) >= velbus.MINIMUM_MESSAGE_SIZE
		assert ord(data[0]) == velbus.START_BYTE
		velbus.logger.info("Processing message %s", " ".join([binascii.hexlify(x) for x in data]))
		if len(data) > velbus.MAXIMUM_MESSAGE_SIZE:
			velbus.logger.warning("Velbus message are maximum %s bytes, this one is %s", str(velbus.MAXIMUM_MESSAGE_SIZE), str(len(data)))
			return
		if ord(data[-1]) != velbus.END_BYTE:
			velbus.logger.warning("end byte not correct")
			return
		priority = ord(data[1])
		if priority != velbus.LOW_PRIORITY and priority != velbus.HIGH_PRIORITY:
			velbus.logger.warning("unrecognized priority")
			return
		address = ord(data[2])
		rtr = (ord(data[3]) & velbus.RTR == velbus.RTR)
		data_size = ord(data[3]) & 0x0F
		if data_size + velbus.MINIMUM_MESSAGE_SIZE != len(data):
			velbus.logger.warning("length of data size does not match actual length of message")
			return
		if not velbus.checksum(data[:-2]) == data[-2]:
			velbus.logger.warning("Packet has no valid checksum")
			return
		if data_size >= 1:
			if velbus.CommandRegistry.has_key(ord(data[4])):
				message = velbus.CommandRegistry[ord(data[4])]()
				message.populate(priority, address, rtr, data[5:-2])
				return message
			else:
				velbus.logger.warning("received unrecognized command %s", str(binascii.hexlify(data[4])))
		else:
			if rtr:
				message = velbus.ModuleTypeRequestMessage()
				message.populate(priority, address, rtr, "")
				return message
			else:
				velbus.logger.warning("zero sized message received without rtr set")