

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


class CorruptResponse(BadResponse):
    pass


class InvalidJsonError(CorruptResponse):
    pass


class MissingResponseError(CorruptResponse):
    pass


class MissingMetaError(CorruptResponse):
    pass
