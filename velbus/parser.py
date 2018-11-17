"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
import velbus


class ParserError(Exception):
    """
    Error when invalid message is received
    """
    pass


class VelbusParser(object):
    """
    Transform Velbus message from wire format to Message object
    """

    def __init__(self, controller):
        assert isinstance(controller, velbus.Controller)
        self.logger = logging.getLogger('velbus')
        self.controller = controller
        self.buffer = bytes([])

    def feed(self, data):
        """
        Add new incoming data to buffer and try to process
        """
        self.buffer += data
        while len(self.buffer) >= 6:
            self.next_packet()

    def valid_header_waiting(self):
        """
        Check if a valid header is waiting in buffer
        """
        if len(self.buffer) < 4:
            self.logger.debug("Buffer does not yet contain full header")
            result = False
        else:
            result = True
            result = result and self.buffer[0] == velbus.START_BYTE
            if not result:
                self.logger.warning("Start byte not recognized")
            result = result and (self.buffer[1] in velbus.PRIORITY)
            if not result:
                self.logger.warning("Priority not recognized")
            result = result and (self.buffer[3] & 0x0F <= 8)
            if not result:
                self.logger.warning("Message size not recognized")
        self.logger.debug("Valid Header Waiting: %s(%s)", result, str(self.buffer))
        return result

    def valid_body_waiting(self):
        """
        Check if a valid body is waiting in buffer
        """
        # 0f f8 be 04 00 08 00 00 2f 04
        packet_size = velbus.MINIMUM_MESSAGE_SIZE + \
            (self.buffer[3] & 0x0F)
        if len(self.buffer) < packet_size:
            self.logger.debug("Buffer does not yet contain full message")
            result = False
        else:
            result = True
            result = result and self.buffer[packet_size - 1] == velbus.END_BYTE
            if not result:
                self.logger.warning("End byte not recognized")
            result = result and velbus.checksum(
                self.buffer[0:packet_size - 2])[0] == self.buffer[packet_size - 2]
            if not result:
                self.logger.warning("Checksum not recognized")
        self.logger.debug("Valid Body Waiting: %s (%s)", result, str(self.buffer))
        return result

    def next_packet(self):
        """
        Process next packet if present
        """
        try:
            start_byte_index = self.buffer.index(velbus.START_BYTE)
        except ValueError:
            self.buffer = bytes([])
            return
        if start_byte_index >= 0:
            self.buffer = self.buffer[start_byte_index:]
        if self.valid_header_waiting() and self.valid_body_waiting():
            next_packet = self.extract_packet()
            self.buffer = self.buffer[len(next_packet):]
            message = self.parse(next_packet)
            if isinstance(message, velbus.Message):
                self.controller.new_message(message)

    def extract_packet(self):
        """
        Extract packet from buffer
        """
        packet_size = velbus.MINIMUM_MESSAGE_SIZE + \
            (self.buffer[3] & 0x0F)
        packet = self.buffer[0:packet_size]
        return packet

    def parse(self, data):
        """
        :return: None
        """
        # pylint: disable-msg=R0911,C1801
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert len(data) >= velbus.MINIMUM_MESSAGE_SIZE
        assert data[0] == velbus.START_BYTE
        self.logger.debug("Processing message %s", str(data))
        if len(data) > velbus.MAXIMUM_MESSAGE_SIZE:
            self.logger.warning("Velbus message are maximum %s bytes, this one is %s", str(
                velbus.MAXIMUM_MESSAGE_SIZE), str(len(data)))
            return
        if data[-1] != velbus.END_BYTE:
            self.logger.warning("end byte not correct")
            return
        priority = data[1]
        if priority not in velbus.PRIORITY:
            self.logger.warning("unrecognized priority")
            return
        address = data[2]
        rtr = data[3] & velbus.RTR == velbus.RTR
        data_size = data[3] & 0x0F
        if data_size + velbus.MINIMUM_MESSAGE_SIZE != len(data):
            self.logger.warning(
                "length of data size does not match actual length of message")
            return
        if not velbus.checksum(data[:-2])[0] == data[-2]:
            self.logger.warning("Packet has no valid checksum")
            return
        if data_size >= 1:
            if data[4] == 0xff:
                message = velbus.ModuleTypeMessage()
                message.populate(priority, address, rtr, data[5:-2])
                return message
            elif address in self.controller._modules:
                command_value = data[4]
                module_type = self.controller.get_module(address).get_type()
                if velbus.commandRegistry.has_command(command_value, module_type):
                    command = velbus.commandRegistry.get_command(command_value, module_type)
                    message = command()
                    message.populate(priority, address, rtr, data[5:-2])
                    return message
                else:
                    self.logger.warning("received unrecognized command %s from module %s (%s)", str(data[4]), str(address), str(module_type))
            else:
                self.logger.warning("received unrecognized command %s from module %s", str(data[4]), str(address))
        else:
            if rtr:
                message = velbus.ModuleTypeRequestMessage()
                message.populate(priority, address, rtr, "")
                return message
            else:
                self.logger.warning("zero sized message received without rtr set")
