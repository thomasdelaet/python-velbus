"""
@author: Thomas Delaet <thomas@delaet.org
"""
import velbus

class VMB6INModule(velbus.Module):
    """
    Velbus input module with 6 channels
    """
    pass

velbus.register_module('VMB6IN', VMB6INModule)
