from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='python-velbus',
      version='2.0.11',
      url='https://bitbucket.org/tdelaet/python-velbus/',
      license='MIT',
      author='Thomas Delaet',
      install_requires=["pyserial==3.3"],
      author_email='thomas@delaet.org',
      description="Python Library for the Velbus protocol",
      long_description=long_description,
      packages=['velbus', 'velbus.config', 'velbus.connections', 'velbus.messages'],
      platforms='any',
      )
