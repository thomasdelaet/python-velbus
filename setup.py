from setuptools import setup

setup(
    name="python-velbus",
    version="2.1.6",
    url="https://github.com/thomasdelaet/python-velbus",
    license="MIT",
    author="Thomas Delaet",
    install_requires=["pyserial>=3.3"],
    author_email="thomas@delaet.org",
    packages=["velbus", "velbus.connections", "velbus.messages", "velbus.modules"],
    include_package_data=True,
)
