"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbusconfig
import velbus

class Controller(object):
	"""
	Velbusconfig coordinator
	"""
	
	def __init__(self, velbus_service):
		assert isinstance(velbus_service, velbus.Controller)
		self.modules = {}
		self.velbus_service = velbus_service
		self.velbus_service.subscribe(self.process_event)
		config_reader = velbusconfig.SwitchConfigReader(self)
		config_reader.read_config()
		
	def add_module(self, module):
		"""
		@return: None
		"""
		assert isinstance(module, velbusconfig.VelbusModule)
		self.modules[module.key()] =  module
	
	def has_module(self, address, channel):
		"""
		@return: bool
		"""
		assert velbusconfig.valid_key(address, channel)
		return self.modules.has_key((address, channel))

	def module(self, address, channel):
		"""
		@return: velbusconfig.VelbusModule
		"""
		assert velbusconfig.valid_key(address, channel)
		assert self.has_module(address, channel)
		return self.modules[(address, channel)]
		
	def process_event(self, event):
		"""
		@return: None
		"""
		assert isinstance(event, velbus.Message)
		if isinstance(event, velbus.PushButtonStatusMessage):
			address = event.address
			for channel in event.get_channels():
				if self.has_module(address, channel):
					module = self.module(address, channel)
					if isinstance(module, velbusconfig.Switch):
						module.toggle_relays()
					if event.is_closed:
						module.set_on()
					if event.is_open:
						module.set_off()
	
	def execute_event(self, event):
		"""
		@return: None
		"""
		assert isinstance(event, velbus.Message)
		self.velbus_service.send(event)