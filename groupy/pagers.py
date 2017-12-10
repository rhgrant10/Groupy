

class Pager:
    """Class for iterating over multiple pages of results.

    This is a generic, base class. To create a specific type of pager, provide
    a definition for ``set_next_page_params`` in a subclass.

    :param manager: the manager from which to get results
    :type manager: :class:`~groupy.api.base.Manager`
    :param func endpoint: a callable from which results can be fetched
    :param kwargs params: initial params to pass to the manager
    """

    #: the base set of params
    default_params = {}

    def __init__(self, manager, endpoint, **params):
        self.manager = manager
        self.endpoint = endpoint
        params = {k: v for k, v in params.items() if v is not None}
        self.params = dict(self.default_params, **params)
        self.items = self.fetch()

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def set_next_page_params(self):
        """Set the params in preparation for fetching the next page."""
        raise NotImplementedError

    def fetch(self):
        """Fetch the current page of results.

        :return: the current page of results
        :rtype: :class:`list`
        """
        return self.endpoint(**self.params)

    def fetch_next(self):
        """Fetch the next page of results.

        :return: the next page of results
        :rtype: :class:`list`
        """
        self.set_next_page_params()
        return self.fetch()

    def autopage(self):
        """Iterate through results from all pages.

        :return: all results
        :rtype: generator
        """
        while self.items:
            yield from self.items
            self.items = self.fetch_next()


class GroupList(Pager):
    """Pager for groups."""

    #: default to the first page
    default_params = {'page': 1}

    def set_next_page_params(self):
        self.params['page'] += 1


class ChatList(GroupList):
    pass


class MessageList(Pager):
    """Pager for messages."""

    def __init__(self, manager, endpoint, **params):
        super().__init__(manager, endpoint, **params)
        self.mode = MessageList.detect_mode(**params)

    @staticmethod
    def detect_mode(**params):
        """Detect which listing mode of the given params.

        :params kwargs params: the params
        :return: one of "before_id", "after_id", or "since_id"
        :rtype: str
        :raises ValueError: if multiple modes are detected
        """
        modes = []
        for mode in ('before_id', 'after_id', 'since_id'):
            if params.get(mode) is not None:
                modes.append(mode)
        if len(modes) > 1:
            raise ValueError('ambiguous mode')
        return modes[0] if modes else 'before_id'

    def set_next_page_params(self):
        if self.items:
            self.params[self.mode] = self.items[-1].id
