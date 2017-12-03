from groupy import utils


class Manager:
    """Class for interacting with the endpoint for a resource.

    :param session: the requests session
    :type session: :class:`~groupy.session.Session`
    :param str path: path relative to the base URL
    """

    #: the base URL
    base_url = 'https://api.groupme.com/v3/'

    def __init__(self, session, path=None):
        self.session = session
        self.url = utils.urljoin(self.base_url, path)


class Resource:
    def __init__(self, **data):
        self.data = data

    def __getattr__(self, attr):
        if attr not in self.data:
            error_message = 'this {!s} resource does not have a {!r} field'
            raise AttributeError(error_message.format(self.__class__.__name__,
                                                      attr))
        return self.data[attr]


class ManagedResource(Resource):
    """Class to represent an API object."""

    def __init__(self, manager, **data):
        """Create an instance of the resource.

        :param manager: the resource's manager
        :type manager: :class:`~groupy.api.base.Manager`
        :param kwargs data: the resource data
        """
        super().__init__(**data)
        self.manager = manager
