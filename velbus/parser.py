"""
:author: Thomas Delaet <thomas@delaet.org>
"""
import logging
from velbus.constants import (
    START_BYTE,
    PRIORITY,
    END_BYTE,
    MINIMUM_MESSAGE_SIZE,
    MAXIMUM_MESSAGE_SIZE,
    RTR,
)
from velbus.util import checksum, VelbusException
from velbus.messages.module_type import ModuleTypeMessage
from velbus.messages.module_subtype import ModuleSubTypeMessage
from velbus.messages.module_type_request import ModuleTypeRequestMessage
from velbus.command_registry import commandRegistry


class VelbusParser(object):
    """
    Transform Velbus message from wire format to Message object
    """

    def __init__(self, controller):
        self.logger = logging.getLogger("velbus")
        self.controller = controller
        self.buffer = bytes([])

    def feed(self, data):
        """
        Add new incoming data to buffer and try to process
        """
        try:
            self.buffer += data
            while len(self.buffer) >= 6:
                self.next_packet()
        except Exception as e:
            self.logger.error("Error while processing received data (%s)", str(self.buffer))
            self.logger.error(e)

    def valid_header_waiting(self):
        """
        Check if a valid header is waiting in buffer
        """
        if len(self.buffer) < 4:
            self.logger.debug("Buffer does not yet contain full header")
            result = False
        else:
            result = True
            result = result and self.buffer[0] == START_BYTE
            if not result:
                self.logger.warning("Start byte not recognized (%s)", str(self.buffer))
            # if self.buffer[1] == START_BYTE:
            #     self.buffer = self.buffer[1:]
            #     self.logger.debug('Duplicate start byte found, discarding first one')
            result = result and (self.buffer[1] in PRIORITY)
            if not result:
                self.logger.warning("Priority not recognized (%s)", str(self.buffer))
            result = result and (self.buffer[3] & 0x0F <= 8)
            if not result:
                self.logger.warning("Message size not recognized (%s)", str(self.buffer))
        self.logger.debug("Valid Header Waiting: %s(%s)", result, str(self.buffer))
        return result

    def valid_body_waiting(self):
        """
        Check if a valid body is waiting in buffer
        """
        # 0f f8 be 04 00 08 00 00 2f 04
        packet_size = MINIMUM_MESSAGE_SIZE + (self.buffer[3] & 0x0F)
        if len(self.buffer) < packet_size:
            self.logger.debug("Buffer does not yet contain full message (%s)", str(self.buffer))
            result = False
        else:
            result = True
            result = result and self.buffer[packet_size - 1] == END_BYTE
            if not result:
                self.logger.warning("End byte not recognized (%s)", str(self.buffer))
            result = (
                result
                and checksum(self.buffer[0 : packet_size - 2])[0]
                == self.buffer[packet_size - 2]
            )
            if not result:
                self.logger.warning("Checksum not recognized (%s)", str(self.buffer))
        self.logger.debug("Valid Body Waiting: %s (%s)", result, str(self.buffer))
        return result

    def next_packet(self):
        """
        Process next packet if present
        """
        try:
            start_byte_index = self.buffer.index(START_BYTE)
        except ValueError:
            self.buffer = bytes([])
            return
        if start_byte_index >= 0:
            self.buffer = self.buffer[start_byte_index:]
        if self.valid_header_waiting() and self.valid_body_waiting():
            next_packet = self.extract_packet()
            self.buffer = self.buffer[len(next_packet) :]
            message = self.parse(next_packet)
            if message is not None:
                self.controller.new_binary_message(message)
        else:
            self.logger.debug("no valid next packet found (%s)", str(self.buffer))
            raise VelbusException('No valid next packet found')

    def extract_packet(self):
        """
        Extract packet from buffer
        """
        packet_size = MINIMUM_MESSAGE_SIZE + (self.buffer[3] & 0x0F)
        packet = self.buffer[0:packet_size]
        return packet

    def parse(self, data):
        """
        :return: None
        """
        # pylint: disable-msg=R0911,C1801
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert len(data) >= MINIMUM_MESSAGE_SIZE
        assert data[0] == START_BYTE
        self.logger.debug("Processing message %s", str(data))
        if len(data) > MAXIMUM_MESSAGE_SIZE:
            self.logger.warning(
                "Velbus message are maximum %s bytes, this one is %s",
                str(MAXIMUM_MESSAGE_SIZE),
                str(len(data)),
            )
            return
        if data[-1] != END_BYTE:
            self.logger.warning("end byte not correct (%s)", str(data))
            return
        priority = data[1]
        if priority not in PRIORITY:
            self.logger.warning("unrecognized priority (%s)", str(data))
            return
        data_size = data[3] & 0x0F
        if data_size + MINIMUM_MESSAGE_SIZE != len(data):
            self.logger.warning(
                "length of data size does not match actual length of message"
            )
            return
        if not checksum(data[:-2])[0] == data[-2]:
            self.logger.warning("Packet has no valid checksum (%s)", str(data))
            return
        if data_size >= 1:
            return data

    def parse_binary_message(self, data):
        assert isinstance(data, bytes)
        priority = data[1]
        address = data[2]
        rtr = data[3] & RTR == RTR
        data_size = data[3] & 0x0F
        if data_size >= 1:
            if data[4] == 0xFF:
                message = ModuleTypeMessage()
                message.populate(priority, address, rtr, data[5:-2])
                return message
            if data[4] == 0xB0:
                message = ModuleSubTypeMessage()
                message.populate(priority, address, rtr, data[5:-2])
                return message
            elif address in self.controller._modules:
                command_value = data[4]
                module_type = self.controller.get_module(address).get_type()
                if commandRegistry.has_command(command_value, module_type):
                    command = commandRegistry.get_command(command_value, module_type)
                    message = command()
                    message.populate(priority, address, rtr, data[5:-2])
                    return message
                else:
                    self.logger.warning(
                        "received unrecognized command %s from module %s (%s)",
                        str(data[4]),
                        str(address),
                        str(module_type),
                    )
            else:
                self.logger.warning(
                    "received unrecognized command %s from module %s",
                    str(data[4]),
                    str(address),
                )
        else:
            if rtr:
                message = ModuleTypeRequestMessage()
                message.populate(priority, address, rtr, "")
                return message
            else:
                self.logger.warning("zero sized message received without rtr set")
