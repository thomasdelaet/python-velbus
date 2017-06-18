"""AsyncIO test."""
import asyncio
import velbus
import logging

device = '/dev/ttyACM0'

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info("start")

loop = asyncio.get_event_loop()

class VelbusStateMachine(velbus.Controller):

    def __init__(self, connection):
        velbus.Controller.__init__(self, connection)
        self._state = {}
        self.subscribe(self.process_event)

    def process_event(self, event):
        print('new event\n')
        print(event.to_json() + '\n'
        if isinstance(event, velbus.RelayStatusMessage):
            if event.address not in self._state:
                self._state[event.address] = {}
            if event.channel not in self._state[event.address]:
                self._state[event.address][event.channel] = False
            self._state[event.address][event.channel] = event.is_on()

    def get_state(self, address, channel):
        if address in self._state and channel in self._state[address]:
            yield self._state[address][channel]
        else:
            yield False


connection = velbus.VelbusUSBConnection(device)
velbus_controller = VelbusStateMachine(connection)
velbus_controller.subscribe(process_event)

print('controller created')

loop.run_forever()
loop.close()

print(connection)
