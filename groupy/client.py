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
    def from_api_token(cls, token):
        session = Session(token=token)
        return cls(session)


"""
token = None
client = Client.from_api_token(token)

groups = client.groups.list()

for group in groups:
    print(group)

for group in groups.autopage():
    print(group)

group = groups[0]
messages = group.messages.list()

for message in messages:
    print(message)

for message in messages.autopage():
    print(message)

"""
