from . import base
from . import messages


class Chats(base.Manager):
    """A chat manager."""

    def __init__(self, session):
        super().__init__(session, 'chats')

    def list(self, **params):
        """List all chats.

        :param kwargs params: any list params
        :return: all chats you have with other users
        :rtype: list
        """
        response = self.session.get(self.url, params=params)
        return [Chat(self, **chat) for chat in response.data]


class Chat(base.Resource):
    """A chat with another user."""

    def __init__(self, manager, **data):
        super().__init__(manager, **data)
        self.messages = messages.DirectMessages(self.manager.session,
                                                self.other_user['id'])

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(other_user={!r})>'.format(klass, self.other_user['name'])

    def post(self, text=None, attachments=None):
        """Post a message to the chat.

        :param str text: the text of the message
        :param list attachments: a list of attachments
        :return: ``True`` if successful
        :rtype: bool
        """
        return self.messages.create(text=text, attachments=attachments)
