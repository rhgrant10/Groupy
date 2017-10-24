from . import base
from . import messages


class Chats(base.Manager):
    def __init__(self, session):
        super().__init__(session, 'chats')

    def list(self, **params):
        response = self.session.get(self.url, params=params)
        return [Chat(self, **chat) for chat in response.data]


class Chat(base.Resource):
    def __init__(self, manager, **data):
        super().__init__(manager, **data)
        self.messages = messages.DirectMessages(self.manager.session,
                                                self.other_user['id'])

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(other_user={!r})>'.format(klass, self.other_user['name'])

    def post(self, *args, **kwargs):
        return self.messages.create(*args, **kwargs)
