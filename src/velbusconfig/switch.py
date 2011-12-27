"""
@author: Thomas Delaet <thomas@delaet.org>
"""

import velbusconfig
import binascii

class Switch(velbusconfig.VelbusModule):
	"""
	A (light) switch
	"""
	
	MAX_CHANNELS = 6
	
	def __init__(self, controller, address, channel):
		assert isinstance(controller, velbusconfig.Controller)
		assert velbusconfig.valid_key(address, channel)
		assert channel <= self.MAX_CHANNELS
		velbusconfig.module.VelbusModule.__init__(self, controller, address, channel)
		self.relays = []
		
	def to_string(self):
		result = binascii.hexlify(chr(self.address)) + " " + str(self.channel) + " : Switch\n"
		for relay in self.relays:
			result += "  " + relay.to_string() + "\n"
		return result
	
	def controls_relay(self, relay):
		"""
		@return: boolean
		"""
		assert isinstance(relay, velbusconfig.Relay)
		return relay in self.relays
	
	def add_relay(self, relay):
		"""
		@return: None
		"""
		assert isinstance(relay, velbusconfig.Relay)
		assert not relay in self.relays
		self.relays.append(relay)
		
	def toggle_relays(self):
		"""
		@return: None
		"""
		print "Toggle Relays from switch " + binascii.hexlify(chr(self.address)) + " " + str(self.channel)
		for relay in self.relays:
			print "  " + relay.to_string() + "\n"
			relay.toggle()