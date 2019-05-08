"""
:author: Thomas Delaet <thomas@delaet.org>
"""

from velbus.controller import Controller


class VelbusConnection(object):
    """
    Generic Velbus connection
    """

    controller = None

    def set_controller(self, controller):
        """
        :return: None
        """
        assert isinstance(controller, Controller)
        self.controller = controller

    def send(self, message, callback=None):
        """
        :return: None
        """
        raise NotImplementedError
