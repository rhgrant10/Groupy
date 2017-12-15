from groupy import utils


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

    #: the default mode param
    default_mode = 'before_id'

    #: all possible mode params and the index for their next page params
    modes = {
        'before_id': -1,
        'after_id': -1,
        'since_id': 0,
    }

    def __init__(self, manager, endpoint, **params):
        super().__init__(manager, endpoint, **params)
        self.mode = self.__class__.detect_mode(**params)

    @classmethod
    def detect_mode(cls, **params):
        """Detect which listing mode of the given params.

        :params kwargs params: the params
        :return: one of the available modes
        :rtype: str
        :raises ValueError: if multiple modes are detected
        """
        modes = []
        for mode in cls.modes:
            if params.get(mode) is not None:
                modes.append(mode)
        if len(modes) > 1:
            error_message = 'ambiguous mode, must be one of {}'
            modes_csv = ', '.join(list(cls.modes))
            raise ValueError(error_message.format(modes_csv))
        return modes[0] if modes else cls.default_mode

    def set_next_page_params(self):
        """Set the params so that the next page is fetched."""
        if self.items:
            index = self.get_last_item_index()
            self.params[self.mode] = self.get_next_page_param(self.items[index])

    def get_last_item_index(self):
        """Return the index of the last item in the page."""
        return self.modes[self.mode]

    def get_next_page_param(self, item):
        """Return the param from the given item.

        :param item: the item that has the next page param
        :returns: next page param value
        """
        return item.id

    def fetch_next(self):
        return super().fetch_next() if self.modes[self.mode] else []


class GalleryList(MessageList):
    """Pager for gallery messages."""

    default_mode = 'before'
    modes = {
        'before': -1,
        'after': -1,
        'since': 0,
    }

    def get_next_page_param(self, item):
        return utils.get_rfc3339(item.created_at)
