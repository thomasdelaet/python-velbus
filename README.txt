This library contains an easy-to-use binding for the Velbus protocol. Currently, all messages of the VMB4RYLD and VMB6IN modules are supported since these are the only two modules I have.

Layout of the velbus library is as follows:
 * The connections dir contains two type of connections that can be the source of velbus messages. These are currently the velbus USB controller and a Netstring connection (more on that later)
 * The messages dir contains all supported message types
 
Dependencies for this library are the simpjeson package (http://simplejson.readthedocs.org/en/latest/) and twisted (http://www.twistedmatrix.com). Install these first.

Install this package is as simple as executing 'python setup.py install' on the command-line.
  
I have included three example scripts that use this library (see examples dir)

SCRIPT 1: forwarder.py

The forwarder script captures all Velbus packets from the physical bus through the USB controller and forwards them using a Netstring protocol (see http://cr.yp.to/proto/netstrings.txt for more information on this protocol).

You can use the velbus.connections.netstring module to capture the packets on another computer and continue processing. I use this to forward packets to Google App Engine where the processing of my home automation system occurs.

What you need to be aware of:
* The forwarder listens on port 8007 (see file forwarder.py in the src/velbus directory to change this)
* To change the device name of your usb controller, see file src/velbus/connections/usb/usb.py and change DEVICE_NAME

SCRIPT 2: switchconfig.py

I have regular pre-home automation switches but want to emulate the behavior of push button switches because my lights are also controlled by other means than switches (for example: the web interface).

To achieve this without buying new switches, I developed the src/velbusconfig python package. 

This package reads a file on startup (currently /etc/velbus_switch_config, see src/velbusconfig/switch_config_reader.py to change this) and uses this to link regular switches to relays.

SCRIPT 3: combination.py 

Different 'services' like the forwarder and switchconfig script can easily be combined because the library uses a publish-subscribe mechanism internally. See combination.py on how the two previous scripts are combined.
