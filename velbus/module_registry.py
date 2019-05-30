"""
:author: Thomas Delaet <thomas@delaet.org>
"""

MODULE_DIRECTORY = {
    0x01: 'VMB8PB',
    0x02: 'VMB1RY',
    0x03: 'VMB1BL',
    0x05: 'VMB6IN',
    0x07: 'VMB1DM',
    0x08: 'VMB4RY',
    0x09: 'VMB2BL',
    0x0a: 'VMB8IR',
    0x0b: 'VMB4PD',
    0x0c: 'VMB1TS',
    0x0d: 'VMB1TH',
    0x0e: 'VMB1TC',
    0x0f: 'VMB1LED',
    0x10: 'VMB4RYLD',
    0x11: 'VMB4RYNO',
    0x12: 'VMB4DC',
    0x13: 'VMBLCDWB',
    0x14: 'VMBDME',
    0x15: 'VMBDMI',
    0x16: 'VMB8PBU',
    0x17: 'VMB6PBN',
    0x18: 'VMB2PBN',
    0x19: 'VMB6PBB',
    0x1a: 'VMB4RF',
    0x1b: 'VMB1RYNO',
    0x1c: 'VMB1BLE',
    0x1d: 'VMB2BLE',
    0x1e: 'VMBGP1',
    0x1f: 'VMBGP2',
    0x20: 'VMBGP4',
    0x21: 'VMBGP0',
    0x22: 'VMB7IN',
    0x28: 'VMBGPOD',
    0x29: 'VMB1RYNOS',
    0x2a: 'VMBIRM',
    0x2b: 'VMBIRC',
    0x2c: 'VMBIRO',
    0x2d: 'VMBGP4PIR',
    0x2e: 'VMB1BLS',
    0x2f: 'VMBDMI-R',
    0x31: 'VMBMETEO',
    0x32: 'VMB4AN',
    0x33: 'VMBVP01',
    0x34: 'VMBEL1',
    0x35: 'VMBEL2',
    0x36: 'VMBEL4',
    0x37: 'VMBELO',
    0x39: 'VMBSIG',
    0x3A: 'VMBGP1-2',
    0x3B: 'VMBGP2-2',
    0x3C: 'VMBGP4-2',
    0x3D: 'VMBGPOD-2',
    0x3E: 'VMBGP4PIR-2'
}

ModuleRegistry = {}

def register_module(module_name, module_class):
    """
    :return: None
    """
    assert isinstance(module_name, str)
    assert isinstance(module_class, type)
    if module_name not in ModuleRegistry:
        ModuleRegistry[module_name] = module_class
    else:
        raise Exception("double registration in module registry")