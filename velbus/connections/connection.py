"""
:author: Thomas Delaet <thomas@delaet.org>
"""

class VelbusConnection(object):
    """
    Generic Velbus connection
    """

    controller = None

    def set_controller(self, controller):
        """
        :return: None
        """
        self.controller = controller

    def send(self, message, callback=None):
        """
        :return: None
        """
        raise NotImplementedError
