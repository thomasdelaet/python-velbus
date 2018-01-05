#!/usr/bin/python3
"""
Example code to scan Velbus and return list of installed modules.
"""

import time
import logging
import sys
import velbus


def scan_completed(modules):
    """Callback when scan is completed."""
    logging.info('Scan completed')
    logging.info(modules)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    #pylint: disable-msg=C0103
    port = '/dev/ttyACM0'
    logging.info('Configuring controller')
    connection = velbus.VelbusUSBConnection(port)
    controller = velbus.Controller(connection)
    logging.info('Starting scan')
    controller.scan(scan_completed)
    logging.info('Starting sleep')
    time.sleep(30)
    logging.info('Exiting ...')
    connection.stop()
