#!/usr/bin/python3
"""
Example code to scan Velbus and return list of installed modules.
"""

import time
import logging
import sys
import velbus


def module_found(module):
    """Callback when new module is found."""
    logging.info('New module')
    logging.info(module._channel_names)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    #pylint: disable-msg=C0103
    port = '/dev/ttyACM0'
    logging.info('Configuring controller')
    connection = velbus.VelbusUSBConnection(port)
    controller = velbus.Controller(connection)
    logging.info('Starting scan')
    controller.scan(module_found)
    logging.info('Starting sleep')
    time.sleep(30)
    logging.info('Exiting ...')
    connection.stop()
