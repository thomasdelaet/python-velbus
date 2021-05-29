#!/usr/bin/python3
"""
Example code to scan Velbus and return list of installed modules.
"""

import time
import logging
import sys
import velbus

def new_module(module, channel):
    print(module)
    print(channel)

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
# pylint: disable-msg=C0103
port = "/dev/velbus"
logging.info("Configuring controller")
controller = velbus.Controller(port)
controller.subscribe_module(new_module, 'switch')
controller.subscribe_module(new_module, 'binary_sensor')
logging.info("Starting scan")
controller.async_scan()
logging.info("Starting sleep")
time.sleep(60*10)
logging.info("Exiting ...")
controller.stop()
