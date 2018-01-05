"""
@author: Thomas Delaet <thomas@delaet.org
"""
import velbus

class VMB4RYModule(velbus.Module):
    """
    Velbus Relay module.
    """
    pass

velbus.register_module('VMB4RYLD', VMB4RYModule)
velbus.register_module('VMB4RYNO', VMB4RYModule)
