

class GroupyError(Exception):
    pass


class ApiError(GroupyError):
    pass


class NoResponse(ApiError):
    def __init__(self, request):
        self.request = request


class BadResponse(ApiError):
    def __init__(self, response):
        self.response = response


class ResultsError(ApiError):
    def __init__(self, response):
        self.response = response


class InvalidJsonError(BadResponse):
    pass


class MissingResponseError(BadResponse):
    pass


class MissingMetaError(BadResponse):
    pass


class ResultsNotReady(ResultsError):
    pass


class ResultsExpired(ResultsError):
    pass
