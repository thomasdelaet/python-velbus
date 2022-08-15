from setuptools import setup

setup(
    name="python-velbus",
<<<<<<< HEAD
    version="2.1.5",
=======
    version="2.1.4",
>>>>>>> 130749faf903ba9fc9190439f3cbeb29487fff3e
    url="https://github.com/thomasdelaet/python-velbus",
    license="MIT",
    author="Thomas Delaet",
    install_requires=["pyserial>=3.3"],
    author_email="thomas@delaet.org",
    packages=["velbus", "velbus.connections", "velbus.messages", "velbus.modules"],
    include_package_data=True,
)
