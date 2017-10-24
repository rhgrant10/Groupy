

class Pager:
    default_params = {}

    def __init__(self, manager, **params):
        self.manager = manager
        self.params = dict(self.default_params, **params)
        self.items = self.fetch()

    def __getitem__(self, index):
        return self.items[index]

    def set_next_page_params(self):
        raise NotImplementedError

    def fetch(self):
        return self.manager._raw_list(**self.params)

    def fetch_next(self):
        self.set_next_page_params()
        return self.fetch()

    def __iter__(self):
        return iter(self.items)

    def autopage(self):
        while self.items:
            yield from self.items
            self.items = self.fetch_next()


class GroupList(Pager):
    default_params = {'page': 1}

    def set_next_page_params(self):
        self.params['page'] += 1


class MessageList(Pager):
    def __init__(self, manager, **params):
        super().__init__(manager, **params)
        self.mode = MessageList.detect_mode(**params)

    @staticmethod
    def detect_mode(**params):
        modes = []
        for mode in ('before_id', 'after_id', 'since_id'):
            if mode in params:
                modes.append(mode)
        if len(modes) > 1:
            raise ValueError('ambiguous mode')
        return modes[0] if modes else 'before_id'

    def set_next_page_params(self):
        if self.items:
            self.params[self.mode] = self.items[-1].id
