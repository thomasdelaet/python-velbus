"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0x02

class SwitchRelayOnMessage(velbus.Message):
	"""
	send by:
	received by: VMB4RYLD
	"""	
	#pylint: disable-msg=R0904
	def __init__(self):
		velbus.Message.__init__(self)
		self.relay_channels = []
		
	def populate(self, priority, address, rtr, data):
		"""
		@return: None
		"""
		assert isinstance(data, str)
		self.needs_high_priority(priority)
		self.needs_no_rtr(rtr)
		self.needs_data(data, 1)
		self.set_attributes(priority, address, rtr)
		self.relay_channels = self.byte_to_channels(data)

	def set_defaults(self, address):
		self.set_address(address)
		self.set_high_priority()
		self.set_no_rtr()
	
	def data_to_binary(self):
		"""
		@return: str
		"""
		return chr(COMMAND_CODE) + self.channels_to_byte(self.relay_channels)
	
velbus.register_command(COMMAND_CODE, SwitchRelayOnMessage)