"""
.. module:: errors
   :platform: Unix, Windows
   :synopsis: Module containing all GroupMe related error classes.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>
"""

class GroupMeError(Exception):
    """A general GroupMe error.
    """
    pass


class InvalidResponseError(GroupMeError):
    """Error representing an unparsable response from the API.
    """
    pass


class InvalidOperatorError(NotImplementedError):
    """Error thrown when an unsupported
    :class:`FilterList<groupy.objects.FilterList>` filter is used.
    """
    pass
