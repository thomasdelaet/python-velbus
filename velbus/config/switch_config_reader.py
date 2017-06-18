"""
@author: Thomas Delaet <thomas@delaet.org>
"""

import json
import os.path
import velbusconfig
import logging


class SwitchConfigReader(object):
    """
    A reader for the configuration file that matches light switches with lights
    """

    def __init__(self, controller):
        assert isinstance(controller, velbusconfig.Controller)
        self.controller = controller

    def read_config(self):
        """
        @return: None
        """
        assert os.path.isfile(self.config_location())
        if os.stat(self.config_location()).st_size == 0:
            return
        handle = open(self.config_location(), 'r')
        config = json.load(handle)
        for entry in config:
            switch_address = entry['switch'][0]
            switch_channel = entry['switch'][1]
            relay_address = entry['relay'][0]
            relay_channel = entry['relay'][1]
            self.create(switch_address, switch_channel,
                        velbusconfig.switch.Switch)
            switch = self.controller.module(switch_address, switch_channel)
            if entry.has_key('is_pushbutton'):
                logging.debug("Setting is_pushbutton to %s for module %s, %s",
                              entry['is_pushbutton'], switch_address, switch_channel)
                switch.is_pushbutton = entry['is_pushbutton']
            self.create(relay_address, relay_channel, velbusconfig.relay.Relay)
            relay = self.controller.module(relay_address, relay_channel)
            self.controller.module(
                switch_address, switch_channel).add_relay(relay)

    def create(self, address, channel, class_):
        """
        Create a new VelbusModule if it does not yet exist

        @return: None
        """
        assert isinstance(class_, type)
        assert issubclass(class_, velbusconfig.VelbusModule)
        assert velbusconfig.valid_key(address, channel)
        if not self.controller.has_module(address, channel):
            module = class_(self.controller, address, channel)
            self.controller.add_module(module)

    def config_location(self):
        """
        @return: str
        """
        # pylint: disable-msg=R0201
        return os.path.join('/etc', 'velbus_switch_config')
