"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import time
import velbus
import logging
import binascii
import threading
import serial
import sys

class VelbusUSBConnection(velbus.VelbusConnection):
		#pylint: disable-msg=R0903
		"""
		Wrapper for SerialPort connection configuration
		"""
	
		DEVICE_NAME = "/dev/cuaU0"
		
		BAUD_RATE = 38400
		
		BYTE_SIZE = serial.EIGHTBITS
		
		PARITY = serial.PARITY_NONE
		
		STOPBITS = serial.STOPBITS_ONE
		
		XONXOFF = 0
		
		RTSCTS = 1
	
		def __init__(self, reactor):
			self.reactor = reactor
			self.serial = serial.Serial(port=self.DEVICE_NAME, baudrate=self.BAUD_RATE, bytesize=self.BYTE_SIZE,
										parity=self.PARITY, stopbits=self.STOPBITS, xonxoff=self.XONXOFF,
										rtscts=self.RTSCTS)		 
			velbus.VelbusConnection.__init__(self)
			reactor.callInThread(self.__read_data)
		
		def __read_data(self):
			while 1:
				data = self.serial.read()
				self.reactor.callFromThread(self.feed_parser, data)				
		
		def feed_parser(self, data):
			assert isinstance(data, str)
			self.controller.feed_parser(data)
					
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
			logging.warning("Sending message on USB bus: %s, %s", str(message), " ".join([binascii.hexlify(x) for x in message.to_binary()]))
			self.serial.write(message.to_binary())
			self.serial.flush()
			time.sleep(float(message.wait_after_send) / float(1000))
			self.controller.new_message(message)