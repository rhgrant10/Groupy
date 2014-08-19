"""
.. module:: objects
   :platform: Unix, Windows
   :synopsis: Module that abstracts the API calls into sensible objects.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

The ``status`` module contains API response status code constants and a method
that returns the textual description of such a constant.

"""

__all__ = [
    'OK', 'CREATED', 'NO_CONTENT', 'NOT_MODIFIED', 'BAD_REQUEST',
    'UNAUTHORIZED', 'FORBIDDEN', 'NOT_FOUND', 'ENHANCE_YOUR_CLAIM',
    'INTERNAL_SERVER_ERROR', 'BAD_GATEWAY', 'SERVICE_UNAVAILABLE',
    'description'
]

OK = 200
"""Success
"""

CREATED = 201
"""Resource was created successfully
"""

NO_CONTENT = 204
"""Resource was deleted successfully
"""

NOT_MODIFIED = 304
"""There was no new data to return
"""

BAD_REQUEST = 400
"""Invalid format or invalid data is specified in the request
"""

UNAUTHORIZED = 401
"""Authentication credentials were missing or incorrect
"""

FORBIDDEN = 403
"""The request was understood, but it has been refused
"""

NOT_FOUND = 404
"""The URI requested is invalid or the requested resource does not exist
"""

ENHANCE_YOUR_CLAIM = 420
"""You are being rate limited
"""

INTERNAL_SERVER_ERROR = 500
"""Something unexpected occurred
"""

BAD_GATEWAY = 502
"""GroupMe is down or being upgraded
"""

SERVICE_UNAVAILABLE = 503
"""The GroupMe servers are up but overloaded with requests
"""


def description(code):
    """Return the text description for a code.

    :param int code: the HTTP status code
    :returns: the text description for the status code
    :rtype: :obj:`str`
    """
    return {
        OK: 'Success!',
        CREATED: 'Resource was created successfully',
        NO_CONTENT: 'Resource was deleted successfully',
        NOT_MODIFIED: 'There was no new data to return',
        BAD_REQUEST: ('Invalid format or invalid data is specified in the '
                      'request'),
        UNAUTHORIZED: 'Authentication credentials were missing or incorrect',
        FORBIDDEN: 'The request was understood, but it has been refused',
        NOT_FOUND: ('The URI requested is invalid or the requested resource '
                    'does not exist'),
        ENHANCE_YOUR_CLAIM: 'You are being rate limited',
        INTERNAL_SERVER_ERROR: 'Something unexpected occurred',
        BAD_GATEWAY: 'GroupMe is down or being upgraded',
        SERVICE_UNAVAILABLE: ('The GroupMe servers are up but overloaded with '
                              'requests')
    }.get(code, '!Unknown!')
