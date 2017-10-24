from .api import bots
from .api import groups
from .api import chats
from .api import user
from .api import images
from .session import Session


class Client:
    def __init__(self, session):
        self.session = session
        self.groups = groups.Groups(self.session)
        self.bots = bots.Bots(self.session)
        self.chats = chats.Chats(self.session)
        self.user = user.User(self.session)
        self.images = images.Images(self.session)

    @classmethod
    def from_token(cls, token):
        session = Session(token=token)
        return cls(session)
