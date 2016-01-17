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

    All exceptions raised by Groupy are descendents of this exception.
    """
    pass


class ApiError(GroupMeError):
    """Error raised when errors are returned in a GroupMe response."""
    pass


class InvalidOperatorError(GroupMeError):
    """Error thrown when an unsupported filter is used.
    """
    pass
