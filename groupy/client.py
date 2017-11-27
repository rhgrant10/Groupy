from .api import bots
from .api import groups
from .api import chats
from .api import user
from .api import attachments
from .session import Session


class Client:
    """The API client.

    The client is the main point of interaction. It can directly list groups,
    chats, bots, and provide your user information. It can also download
    the image of a message attachment.

    :param session: the request session
    :type session: :class:`~groupy.session.Session`
    """

    def __init__(self, session):
        self.session = session
        self.groups = groups.Groups(self.session)
        self.chats = chats.Chats(self.session)
        self.bots = bots.Bots(self.session)
        self.user = user.User(self.session)
        self.images = attachments.Images(self.session)

    @classmethod
    def from_token(cls, token):
        """Create a client directly from an API token.

        :param str token: an API token
        :return: a client
        :rtype: :class:`~groupy.client.Client`
        """
        session = Session(token=token)
        return cls(session)
