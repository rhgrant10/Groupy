"""
.. module:: errors
   :platform: Unix, Windows
   :synopsis: Module containing all GroupMe related error classes.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

The ``error`` module contains all of the exceptions thrown by the
GroupMe API.

"""

class GroupMeError(Exception):
    """A general GroupMe error.
    """
    pass


class InvalidResponseError(GroupMeError):
    """Error representing an unparsable response from the API.
    """
    pass


class ApiError(GroupMeError):
    pass


class InvalidOperatorError(NotImplementedError):
    """Error thrown when an unsupported filter is used.
    """
    pass
