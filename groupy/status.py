OK = 200
CREATED = 201
NO_CONTENT = 204
NOT_MODIFIED = 304
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
ENHANCE_YOUR_CLAIM = 420
INTERNAL_SERVER_ERROR = 500
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503


def description(code):
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
