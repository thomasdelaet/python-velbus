"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xda

class BusErrorCounterStatusMessage(velbus.Message):
	"""
	send by: VMB6IN, VMB4RYLD
	received by:
	"""	
	def __init__(self):
		velbus.Message.__init__(self)
		self.transmit_error_counter = 0
		self.receive_error_counter = 0
		self.bus_off_counter = 0
		
	def populate(self, priority, address, rtr, data):
		"""
		@return ""
		"""
		assert isinstance(data, str)
		self.needs_low_priority(priority)
		self.needs_no_rtr(rtr)
		self.needs_data(data, 3)
		self.transmit_error_counter = ord(data[0])
		self.receive_error_counter = ord(data[1])
		self.bus_off_counter = ord(data[2])
			
	def data_to_binary(self):
		"""
		@return: str
		"""
		return chr(COMMAND_CODE) + chr(self.transmit_error_counter) + \
			chr(self.receive_error_counter) + chr(self.bus_off_counter)
					
velbus.register_command(COMMAND_CODE, BusErrorCounterStatusMessage)