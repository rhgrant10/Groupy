

class GroupyError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ApiError(GroupyError):
    pass


class NoResponse(ApiError):
    def __init__(self, request, message='Could not get a response'):
        super().__init__(message)
        self.request = request


class BadResponse(ApiError):
    def __init__(self, response, message='Got a bad response'):
        super().__init__(message)
        self.response = response


class InvalidJsonError(BadResponse):
    pass


class MissingResponseError(BadResponse):
    pass


class MissingMetaError(BadResponse):
    pass


class ResultsError(ApiError):
    def __init__(self, response, message):
        super().__init__(message)
        self.response = response


class ResultsNotReady(ResultsError):
    def __init__(self, response, message='The results are not ready yet'):
        super().__init__(response, message)


class ResultsExpired(ResultsError):
    def __init__(self, response, message='The results have expired'):
        super().__init__(response, message)
