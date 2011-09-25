"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xd9

class BusErrorStatusRequestMessage(velbus.Message):
	"""
	send by: 
	received by: VMB6IN, VMB4RYLD
	"""	
	def __init__(self):
		velbus.Message.__init__(self)
		
	def populate(self, priority, address, rtr, data):
		"""
		@return ""
		"""
		assert isinstance(data, str)
		self.needs_low_priority(priority)
		self.needs_no_rtr(rtr)
		self.needs_no_data(data)
		self.set_attributes(priority, address, rtr)
			
	def data_to_binary(self):
		"""
		@return: str
		"""
		return chr(COMMAND_CODE)
	
velbus.register_command(COMMAND_CODE, BusErrorStatusRequestMessage)
