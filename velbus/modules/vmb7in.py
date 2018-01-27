"""
:author: Thomas Delaet <thomas@delaet.org
"""
import velbus

class VMB7INModule(velbus.modules.VMB6INModule):
    """
    Velbus input module with 7 channels
    """
    def number_of_channels(self):
        return 8

velbus.register_module('VMB7IN', VMB7INModule)
