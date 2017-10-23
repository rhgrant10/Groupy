from . import managers
from .session import Session


class Client:
    def __init__(self, session):
        self.session = session
        self.groups = managers.Groups(self.session)
        self.bots = managers.Bots(self.session)
        self.chats = managers.Chats(self.session)
        self.user = managers.User(self.session)
        self.images = managers.Images(self.session)

    @classmethod
    def from_token(cls, token):
        session = Session(token=token)
        return cls(session)
