#!/usr/bin/env python

"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import twisted.internet.reactor
import velbus
import sys

class Controller(object):
    #pylint: disable-msg=R0903
    """
    Controller object for Velbus forwarder instance
    """
    def __init__(self):
        #pylint: disable-msg=E1101
        velbus_connection = velbus.VelbusUSBConnection(twisted.internet.reactor)
        self.velbus_controller = velbus.Controller(velbus_connection)
        twisted.internet.reactor.callWhenRunning(self.execute_command)
        twisted.internet.reactor.run()
        
    def execute_command(self):
        message = None
        print sys.argv
        if sys.argv[0] == "on":
            message = velbus.SwitchRelayOnMessage()
        elif sys.argv[1] == "off":
            message = velbus.SwitchRelayOffMessage()
        message.populate(velbus.HIGH_PRIORITY, ord(binascii.unhexlify(sys.argv[2])), bool(velbus.NO_RTR), sys.argv[3])
        self.velbus_controller.send(message)
        twisted.internet.reactor.callLater(1, self.stop)
    
    def stop(self):
        twisted.internet.reactor.stop()
    
if __name__ == "__main__":
    Controller()