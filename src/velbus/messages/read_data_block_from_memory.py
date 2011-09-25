"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xc9

class ReadDataBlockFromMemoryMessage(velbus.Message):
	"""
	send by: 
	received by: VMB4RYLD
	"""	
	def __init__(self):
		velbus.Message.__init__(self)
		self.high_address = 0x00
		self.low_address = 0x00
		
	def populate(self, priority, address, rtr, data):
		"""
		@return ""
		"""
		assert isinstance(data, str)
		self.needs_low_priority(priority)
		self.needs_no_rtr(rtr)
		self.needs_data(data, 2)
		self.set_attributes(priority, address, rtr)
		self.low_address = ord(data[1])
		self.high_address = ord(data[0])
			
	def data_to_binary(self):
		"""
		@return: str
		"""
		return chr(COMMAND_CODE) + chr(self.high_address) + \
			chr(self.low_address)
					
velbus.register_command(COMMAND_CODE, ReadDataBlockFromMemoryMessage)