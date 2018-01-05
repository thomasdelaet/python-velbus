"""
@author: Thomas Delaet <thomas@delaet.org
"""
import velbus

class VMB6INModule(velbus.Module):
    """
    Velbus input module with 6 channels
    """
    def number_of_channels(self):
        return 7

velbus.register_module('VMB6IN', VMB6INModule)
