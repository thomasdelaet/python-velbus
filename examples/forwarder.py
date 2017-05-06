#!/usr/bin/env python

"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import logging
import sys

class Controller(object):
    # pylint: disable-msg=R0903
    """
    Controller object for Velbus forwarder instance
    """

    def __init__(self):
        # pylint: disable-msg=E1101
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info("start reactor")
        sys.stdout.write("start\n")
        velbus_connection = velbus.VelbusUSBConnection(
            twisted.internet.reactor, '/dev/ttyACM0')
        velbus_controller = velbus.Controller(velbus_connection)
        #self.forwarder = velbus.VelbusForwarder(velbus_controller, twisted.internet.reactor)
        twisted.internet.reactor.run()


if __name__ == "__main__":
    Controller()
