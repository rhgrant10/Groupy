from . import utils


class Manager:
    base_url = 'https://api.groupme.com/v3/'

    def __init__(self, session, path=None):
        self.session = session
        self.url = utils.urljoin(self.base_url, path)


class Resource:
    def __init__(self, manager, **data):
        self.manager = manager
        self.data = data

    def __getattr__(self, attr):
        if attr not in self.data:
            error_message = '{!s} resources do not have a {!r} field'
            raise AttributeError(error_message.format(self.__class__.__name__,
                                                      attr))
        return self.data[attr]
