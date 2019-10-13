## python-velbus: A python library to control the Velbus home automation system

This library was created to support the Velbus protocol in my home automation efforts.

It is currently being used by the Velbus component in [home assisstant](http://home-assistant.io) but can also be used indepenently.

The latest version of the library is published as a python package on [pypi](https://pypi.python.org/pypi/python-velbus)

I would like to extend this module to support all Velbus modules, so feel free to submit pull requests or log issues through [github](http://www.github.com/thomasdelaet/python-velbus) for functionality you like to have included.

API documentation is available [here](http://python-velbus.readthedocs.io/en/latest/)

# Example usage

The library currently only supports a serial connection to the Velbus controller (either through USB module or through RS-232 interface). In order to use the library, you need to first initialize the controller and can then send and receive messages on the Velbus. The library currently does not validate if a message is supported by a certain module (e.g., you can send a blind up message to a relay)

```python
import velbus
import time

# serial (or USB over serial) device connected to Velbus controller
port = "/dev/ttyACM0"

connection = velbus.VelbusUSBConnection(port)
controller = velbus.Controller(connection)
controller.subscribe(_on_message)

# set module address
module_address = 0xdc
message = velbus.SwitchRelayOnMessage(module_address)

channel_number = 1

message.relay_channels = [channel_number]

controller.send(message)

def _on_message(received_message):
    print("Velbus message received")
    print(received_message.address)

time.sleep(5)

connection.stop()
```

# Installation

You can install the library with pip (*pip install python-velbus*) or by checking out the [github](https://github.com/thomasdelaet/python-velbus) repository and running *python setup.py install* at the root of the repository.

# Supported modules

The following Velbus modules are currently supported by this library:

| Module name | Description | Status | Comments |
| ----------- | ----------- | ------ | -------- |
| VMB1BL | 1 channel blind module | SUPPORTED | All messages are supported |
| VMB1RS | Serial interface | SUPPORTED | All messages are supported |
| VMB1RYNO | 1 channel relay module | SUPPORTED | All messages are supported |
| VMB1RYNOS | 1 channel relay module | SUPPORTED | All messages are supported |
| VMB1TS | 1 channel temperatue sensor | SUPPORTED | Temperature supported |
| VMB1USB | USB configuration module | SUPPORTED | All messages are supported |
| VMB2BL | 2 channel blind module | SUPPORTED | All messages are supported |
| VMB2BLE | 2 channel blind module | SUPPORTED | All messages are supported |
| VMB2PBN | 2 channel input module | SUPPORTED | All messages are supported |
| VMB4DC | 4 channel 0-10 dimmer module | SUPPORTED | All messages are supported |
| VMB4RY | 4 channel relay module | SUPPORTED | All messages are supported |
| VMB4RYLD | 4 channel relay module | SUPPORTED | All messages are supported |
| VMB4RYNO | 4 channel relay module | SUPPORTED | All messages are supported |
| VMB6IN | 6 channel input module | SUPPORTED | All messages are supported |
| VMB6PBN | 6 channel input module | SUPPORTED | All messages are supported |
| VMB7IN | 7 channel input module | SUPPORTED | All messages are supported |
| VMB8PBU | 8 channel input module | SUPPORTED | All messages are supported |
| VMBDME | 1 channel dimmer module | SUPPORTED | All messages are supported |
| VMBGP1 | 1 channel glass panel | SUPPORTED | Input and Temperature supported |
| VMBGP2 | 2 channel glass panel | SUPPORTED | Input and Temperature supported |
| VMBGP4 | 4 channel glass panel | SUPPORTED | Input and Temperature supported |
| VMBGPO | 72 channel glass panel with oled | SUPPORTED | Input and Temperature supported |
| VMBGPOD | 72 channel glass panel with oled and thermostat | SUPPORTED | Input and Temperature supported |
| VMBMETEO | meteo modules | SUPPORTED | Temperature, wind, rain and light sensor supported |
| VMBRSUSB | Configuration module with USB and RS-232 interface | SUPPORTED | All messages are supported |

# Adding support for other modules

The [velbus website](http://www.velbus.eu) contains an overview of the different available modules and their protocol documentation. In order to add support for an additional module, read through the protocol documemntation and add support for missing messages (many messages are shared between modules so make sure to check if a message already exists or not)

Steps to add support for an additional module:

- [ ] Look up the protocol documentation of the module you want to include at the [velbus website](https://www.velbus.eu/products/): Select the module, go to *Downloads* and search for the info sheet with protocol information.
- [ ] Go through the messages directory and look for messages in the protocol information sheet that are not yet supported. Create a new file in the *messages* folder for each unsupported message. Every new message should inherit from the *Message* object and reuse common functionality.
- [ ] Implement constructor method for each new message
- [ ] Implement the *populate* and *data_to_binary* methods for each new message
- [ ] If the message has other than low priority or no RTR set (which are defaults), then re-implement *set_defaults* method
- [ ] Add new messages to the *__init__.py* file in the *messages* folder
- [ ] Test and iterate
- [ ] Update the Supported modules section of the *README.md* file
- [ ] Submit a pull request on Github

# Further development

The library currently offers only the lowest level of functionality: sending and receiving messages to modules. I plan to extend this library with more higher-level functionality such as:

- [x] Modeling modules and their supported functions as entities
- [ ] Only allowing to send supported messages to modules
- [x] Auto-discovery of modules
- [ ] Exposing the velbus controller as an external API so it can be shared between different consumers
