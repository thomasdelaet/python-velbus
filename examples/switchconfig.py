#!/usr/bin/env python

"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import twisted.internet.reactor
import velbus
import velbusconfig

class Controller(object):
	#pylint: disable-msg=R0903
	"""
	Controller object for Velbus forwarder instance
	"""
	def __init__(self):
		#pylint: disable-msg=E1101
		velbus_connection = velbus.VelbusUSBConnection(twisted.internet.reactor)
		velbus_controller = velbus.Controller(velbus_connection)
		self.velbus_config = velbusconfig.Controller(velbus_controller)
		twisted.internet.reactor.run()
	
if __name__ == "__main__":
	Controller()