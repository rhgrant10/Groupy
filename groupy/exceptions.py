

class GroupyError(Exception):
    """Base exception for all Groupy exceptions.

    :param str message: a description of the exception
    """
    #: a description of the exception
    message = None

    def __init__(self, message=None):
        self.message = message or self.message
        super().__init__(self.message)


class MissingMembershipError(GroupyError):
    """Exception raied when your membership could not be found in a group."""
    message = ('The group does not contain your membership; if not a former '
               'group, try refreshing the group.')

    def __init__(self, group_id, user_id, message=None):
        super().__init__(message)
        self.group_id = group_id
        self.user_id = user_id


class FindError(GroupyError):
    """Exception raised when the number of results is not 1."""

    def __init__(self, message, objects, tests, matches=None):
        super().__init__(message)
        self.objects = objects
        self.tests = tests
        self.matches = matches


class NoMatchesError(FindError):
    """Exception raised when the number of results is 0."""

    def __init__(self, objects, tests):
        message = 'No matches using {!r}'.format(tests)
        super().__init__(message, objects, tests)


class MultipleMatchesError(FindError):
    """Exception raised when the number of results exceeds 1."""

    def __init__(self, objects, tests, matches):
        message = 'Found {} matches using {!r}'.format(len(matches), tests)
        super().__init__(message, objects, tests, matches)


class ApiError(GroupyError):
    """Base exception for all GroupMe API errors."""
    message = 'There was a problem communicating with the API.'


class NoResponse(ApiError):
    """Exception raised when the API server could not be reached.

    :param request: the original request that was made
    :type request: :class:`~requests.PreparedRequest`
    :param str message: a description of the exception
    """

    message = 'Could not get a response'

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request


class BadResponse(ApiError):
    """Exception raised when the status code of the response was 400 or more.

    :param response: the response
    :type response: :class:`~requests.Response`
    :param str message: a description of the exception
    """

    message = 'Got a bad response'

    def __init__(self, response, message=None):
        if message is None:
            message = self._extract_message(response)
        super().__init__(message=message)
        self.response = response

    def _extract_message(self, response):
        try:
            meta = response.json()['meta']
            code = meta.get('code', response.status_code)
            errors = ','.join(meta.get('errors', ['unknown']))
        except (ValueError, KeyError):
            return None
        return 'HTTP {code}: {errors}'.format(code=code, errors=errors)


class InvalidJsonError(BadResponse):
    """Exception raised for incomplete/invalid JSON in a response."""

    def __init__(self, response, message='The JSON was incomplete/invalid'):
        super().__init__(response, message)


class MissingResponseError(BadResponse):
    """Exception raised for a response that lacks response data."""

    def __init__(self, response, message='The response contained no response data'):
        super().__init__(response, message)


class MissingMetaError(BadResponse):
    """Exception raised for a response that lacks meta data."""

    def __init__(self, response, message='The response contained no meta data'):
        super().__init__(response, message)


class ResultsError(ApiError):
    """Exception raised for asynchronous results.

    :param response: the response
    :type response: :class:`~requests.Response`
    :param str message: a description of the exception
    """

    def __init__(self, response, message):
        super().__init__(message)
        self.response = response


class ResultsNotReady(ResultsError):
    """Exception raised when results are not yet ready.

    :param response: the response
    :type response: :class:`~requests.Response`
    :param str message: a description of the exception
    """

    def __init__(self, response, message='The results are not ready yet'):
        super().__init__(response, message)


class ResultsExpired(ResultsError):
    """Exception raised when the results have expired.

    :param response: the response
    :type response: :class:`~requests.Response`
    :param str message: a description of the exception
    """

    def __init__(self, response, message='The results have expired'):
        super().__init__(response, message)
