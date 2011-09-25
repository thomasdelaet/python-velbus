from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='python-velbus',
		version='1.0',
		py_modules=[''],
		description="Python Library for the Velbus protocol",
		author='Thomas Delaet',
		author_email='thomas@delaet.org',
		url='https://bitbucket.org/tdelaet/python-velbus/',
		package_dir= {'': 'src'},
		packages=['velbus', 'velbusconfig', "velbus.messages", 'velbus.connections.netstring', 'velbus.connections.usb'],
		long_description=long_description
		)