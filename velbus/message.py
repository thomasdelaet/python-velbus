"""
@author: Thomas Delaet <thomas@delaet.org>
"""
import velbus
import json
import base64


class Message(object):
    # pylint: disable-msg=R0921,R0904
    """
    Base Velbus message
    """

    def __init__(self):
        self.priority = None
        self.address = None
        self.rtr = False
        self.wait_after_send = 100

    def set_attributes(self, priority, address, rtr):
        """
        @return: None
        """
        assert isinstance(priority, int)
        assert isinstance(address, int)
        assert isinstance(rtr, bool)
        assert priority == velbus.HIGH_PRIORITY or priority == velbus.LOW_PRIORITY
        assert address >= velbus.LOW_ADDRESS and address <= velbus.HIGH_ADDRESS
        self.priority = priority
        self.address = address
        self.rtr = rtr

    def populate(self, priority, address, rtr, data):
        """
        @return: None
        """
        raise NotImplementedError

    def set_defaults(self, address):
        """
        @return: None
        """
        raise NotImplementedError

    def set_address(self, address):
        """
        @return: None
        """
        assert isinstance(address, int)
        self.address = address

    def to_binary(self):
        """
        @return: bytes
        """
        pre_checksum_data = self.__checksum_data()
        checksum = velbus.checksum(pre_checksum_data)
        return pre_checksum_data + checksum + bytes([velbus.END_BYTE])

    def to_base64(self):
        """
        @return: str
        """
        return base64.b64encode(self.to_binary())

    def __checksum_data(self):
        """
        @return: bytes
        """
        data_bytes = self.data_to_binary()
        if self.rtr:
            rtr_and_size = velbus.RTR | len(data_bytes)
        else:
            rtr_and_size = len(data_bytes)
        prefix = bytes([velbus.START_BYTE, self.priority, self.address,
                        rtr_and_size])
        return prefix + data_bytes

    def data_to_binary(self):
        """
        @return: bytes
        """
        raise NotImplementedError

    def to_json_basic(self):
        return {'name': self.__class__.__name__, 'priority': self.priority,
                'address': self.address, 'rtr': self.rtr}

    def to_json(self):
        """
        @return: str
        """
        # FIXME: Implement in subclasses
        return json.dumps(self.to_json_basic())

    def __str__(self):
        return self.to_json()

    def byte_to_channels(self, byte):
        """
        @return: list(int)
        """
        # pylint: disable-msg=R0201
        assert isinstance(byte, int)
        assert(byte >= 0)
        assert(byte < 256)
        result = []
        for offset in range(0, 8):
            if byte & (1 << offset):
                result.append(offset + 1)
        return result

    def channels_to_byte(self, channels):
        """
        @return: int
        """
        # pylint: disable-msg=R0201
        assert isinstance(channels, list)
        result = 0
        for offset in range(0, 8):
            if offset + 1 in channels:
                result = result + (1 << offset)
        return result

    def byte_to_channel(self, byte):
        """
        @return: int
        """
        assert isinstance(byte, int)
        channels = self.byte_to_channels(byte)
        self.needs_one_channel(channels)
        return channels[0]

    def needs_valid_channel(self, channel, maximum):
        """
        @return: None
        """
        assert isinstance(channel, int)
        assert isinstance(maximum, int)
        if channel < 1 and channel > maximum:
            self.parser_error("needs valid channel in channel byte")

    def parser_error(self, message):
        """
        @return: None
        """
        raise velbus.ParserError(self.__class__.__name__ + " " + message)

    def needs_rtr(self, rtr):
        """
        @return: None
        """
        assert isinstance(rtr, bool)
        if not rtr:
            self.parser_error("needs rtr set")

    def set_rtr(self):
        """
        @return: None
        """
        self.rtr = True

    def needs_no_rtr(self, rtr):
        """
        @return: None
        """
        assert isinstance(rtr, bool)
        if rtr:
            self.parser_error("does not need rtr set")

    def set_no_rtr(self):
        """
        @return: None
        """
        self.rtr = False

    def needs_low_priority(self, priority):
        """
        @return: None
        """
        assert isinstance(priority, int)
        if priority != velbus.LOW_PRIORITY:
            self.parser_error("needs low priority set")

    def set_low_priority(self):
        """
        @return: None
        """
        self.priority = velbus.LOW_PRIORITY

    def needs_high_priority(self, priority):
        """
        @return: None
        """
        assert isinstance(priority, int)
        if priority != velbus.HIGH_PRIORITY:
            self.parser_error("needs high priority set")

    def set_high_priority(self):
        """
        @return: None
        """
        self.priority = velbus.HIGH_PRIORITY

    def needs_no_data(self, data):
        """
        @return: None
        """
        if len(data) != 0:
            self.parser_error("has data included")

    def needs_data(self, data, length):
        """
        @return: None
        """
        assert isinstance(data, bytes)
        if len(data) != length:
            self.parser_error("needs " + str(length) + " bytes of data")

    def needs_fixed_byte(self, byte, value):
        """
        @return: None
        """
        assert isinstance(byte, int)
        assert isinstance(value, int)
        assert byte >= 0 and value >= 0
        assert byte <= 0xff and value <= 0xff
        if byte != value:
            self.parser_error("expects " + chr(value) +
                              " in byte " + chr(byte))

    def needs_one_channel(self, channels):
        """
        @return: None
        """
        assert isinstance(channels, list)
        if len(channels) != 1 or not isinstance(channels[0], int) or \
                not channels[0] > 0 or not channels[0] <= 8:
            self.parser_error("needs exactly one bit set in channel byte")
