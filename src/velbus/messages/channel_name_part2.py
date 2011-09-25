"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus

COMMAND_CODE = 0xf1

class ChannelNamePart2Message(velbus.Message):
	"""
	send by: VMB6IN, VMB4RYLD
	received by:
	"""	
	def __init__(self):
		velbus.Message.__init__(self)
		self.channel = 0
		self.name = ""
		
	def populate(self, priority, address, rtr, data):
		"""
		@return ""
		"""
		assert isinstance(data, str)
		self.needs_low_priority(priority)
		self.needs_no_rtr(rtr)
		self.needs_data(data, 7)
		self.set_attributes(priority, address, rtr)
		channels = self.byte_to_channels(data[0])
		self.needs_one_channel(channels)
		self.channel = channels[0]
		self.name = data[1:]		

	def data_to_binary(self):
		"""
		@return: str
		"""
		return chr(COMMAND_CODE) + self.channels_to_byte([self.channel]) + \
			self.name
					
velbus.register_command(COMMAND_CODE, ChannelNamePart2Message)