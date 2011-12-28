"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import twisted.internet.serialport
from velbus.connections.usb.protocol import VelbusProtocol
import time
import velbus
import logging
import binascii

class VelbusUSBConnection(velbus.VelbusConnection):
		#pylint: disable-msg=R0903
		"""
		Wrapper for SerialPort connection configuration
		"""
	
		DEVICE_NAME = "/dev/usb/ttyUSB0"
		
		BAUD_RATE = 38400
		
		BYTE_SIZE = twisted.internet.serialport.EIGHTBITS
		
		PARITY = twisted.internet.serialport.PARITY_NONE
		
		STOPBITS = twisted.internet.serialport.STOPBITS_ONE
		
		XONXOFF = 0
		
		RTSCTS = 1
	
		def __init__(self, reactor):
			velbus.VelbusConnection.__init__(self)
			self.protocol = VelbusProtocol(self)
			device_name = self.DEVICE_NAME
			baudrate = self.BAUD_RATE
			bytesize = self.BYTE_SIZE
			parity = self.PARITY
			stopbits = self.STOPBITS
			xonxoff = self.XONXOFF
			rtscts = self.RTSCTS
			self.serial = twisted.internet.serialport.SerialPort(self.protocol, 
															 device_name, 
															 reactor, 
															 baudrate, 
															 bytesize, 
															 parity, 
															 stopbits, 
															 xonxoff, 
															 rtscts)
					
		def split_in_messages(self, data):
			"""
			@return: None
			"""
			assert isinstance(data, str)
			self.controller.split_in_messages(data)
		
		def send(self, message):
			"""
			@return: None
			"""
			assert isinstance(message, velbus.Message)
			logging.debug("Sending message on USB bus: %s, %s", str(message), " ".join([binascii.hexlify(x) for x in message.to_binary()]))
			self.protocol.write(message.to_binary())
			time.sleep(float(message.wait_after_send) / float(1000))
			self.controller.new_message(message)