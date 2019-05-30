import os
from velbus.constants import MINIMUM_MESSAGE_SIZE, MAXIMUM_MESSAGE_SIZE

def on_app_engine():
    """
    :return: bool
    """
    if 'SERVER_SOFTWARE' in os.environ:
        server_software = os.environ['SERVER_SOFTWARE']
        if server_software.startswith('Google App Engine') or \
                server_software.startswith('Development'):
            return True
        return False
    return False

def checksum(data):
    """
    :return: int
    """
    assert isinstance(data, bytes)
    assert len(data) >= MINIMUM_MESSAGE_SIZE - 2
    assert len(data) <= MAXIMUM_MESSAGE_SIZE - 2
    __checksum = 0
    for data_byte in data:
        __checksum += data_byte
    __checksum = -(__checksum % 256) + 256
    try:
        __checksum = bytes([__checksum])
    except ValueError:
        __checksum = bytes([0])
    return __checksum


class VelbusException(Exception):
    """Velbus Exception."""
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)