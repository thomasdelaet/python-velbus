"""
@author: Thomas Delaet <thomas@delaet.org
"""
import velbus

class VMB7INModule(velbus.Module):
    """
    Velbus input module with 7 channels
    """
    pass

velbus.register_module('VMB7IN', VMB7INModule)
