#!/usr/bin/python3
"""
Example code to scan Velbus and return list of installed modules.
"""

import time
import logging
import sys
import velbus


def scan_finished():
    """
    Callback for finished scan
    """
    logging.info(controller.get_modules('switch'))
    logging.info(controller.get_modules('binary_sensor'))


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#pylint: disable-msg=C0103
port = '/dev/ttyACM0'
logging.info('Configuring controller')
connection = velbus.VelbusUSBConnection(port)
controller = velbus.Controller(connection)
logging.info('Starting scan')
controller.scan(scan_finished)
logging.info('Starting sleep')
time.sleep(30)
logging.info('Exiting ...')
connection.stop()
