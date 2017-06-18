"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import velbusconfig
import binascii
import logging


class Relay(velbusconfig.VelbusModule):
    """
    One individual relay as a channel on a relay module
    """

    def to_string(self):
        return binascii.hexlify(chr(self.address)) + " " + str(self.channel) + " : Relay"

    def toggle(self):
        """
        @return: None
        """
        if self.is_on:
            self.send_off_message()
        else:
            self.send_on_message()

    def send_off_message(self):
        """
        @return: None
        """
        message = velbus.SwitchRelayOffMessage()
        logging.debug("Sending off message for channel %s", self.channel)
        message.populate(velbus.HIGH_PRIORITY, self.address,
                         bool(velbus.NO_RTR), message.channels_to_byte([self.channel]))
        self.controller.execute_event(message)

    def send_on_message(self):
        """
        @return: None
        """
        message = velbus.SwitchRelayOnMessage()
        logging.debug("Sending on message for channel %s", self.channel)
        message.populate(velbus.HIGH_PRIORITY, self.address,
                         bool(velbus.NO_RTR), message.channels_to_byte([self.channel]))
        self.controller.execute_event(message)
