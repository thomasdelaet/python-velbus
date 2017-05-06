"""AsyncIO test."""
import asyncio
import velbus
import logging

device = '/dev/ttyACM0'

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info("start")

loop = asyncio.get_event_loop()

def process_event(event):
    print('new event\n')
    print(event.to_json() + '\n')


connection = velbus.VelbusUSBConnection(device)
velbus_controller = velbus.Controller(connection)
velbus_controller.subscribe(process_event)

print('controller created')

loop.run_forever()
loop.close()

print(connection)
