import time
from datetime import datetime

from . import base
from groupy import utils
from groupy import pagers


class Messages(base.Manager):
    def __init__(self, session, group_id):
        path = 'groups/{}/messages'.format(group_id)
        super().__init__(session, path=path)

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        messages = response.data['messages']
        return [Message(self, **message) for message in messages]

    def list(self, **params):
        return pagers.MessageList(self, **params)

    def list_before(self, message_id, **params):
        return self.list(before_id=message_id, **params)

    def list_since(self, message_id, **params):
        return self.list(since_id=message_id, **params)

    def list_after(self, message_id, **params):
        return self.list(after_id=message_id, **params)

    def create(self, text=None, attachments=None, source_guid=None):
        message = {
            'source_guid': source_guid or str(time.time()),
        }

        if text is not None:
            message['text'] = text

        if attachments is not None:
            message['attachments'] = [a.to_json() for a in attachments]

        payload = {'message': message}
        response = self.session.post(self.url, json=payload)
        message = response.data['message']
        return Message(self, **message)


class DirectMessages(base.Manager):
    def __init__(self, session, other_user_id):
        super().__init__(session, 'direct_messages')
        self.other_user_id = other_user_id

    def _raw_list(self, **params):
        params['other_user_id'] = self.other_user_id
        response = self.session.get(self.url, params=params)
        messages = response.data['direct_messages']
        return [DirectMessage(self, **message) for message in messages]

    def list(self, **params):
        return pagers.MessageList(self, **params)

    def list_before(self, message_id, **kwargs):
        return self.list(before_id=message_id, **kwargs)

    def list_since(self, message_id, **kwargs):
        return self.list(since_id=message_id, **kwargs)

    def create(self, text=None, attachments=None, source_guid=None):
        message = {
            'source_guid': source_guid or str(time.time()),
            'recipient_id': self.other_user_id,
        }

        if text is not None:
            message['text'] = text

        if attachments is not None:
            message['attachments'] = attachments

        payload = {'direct_message': message}
        response = self.session.post(self.url, json=payload)
        message = response.data['direct_message']
        return DirectMessage(self, **message)


class GenericMessage(base.Resource):
    preview_length = 42

    def __init__(self, manager, conversation_id, **data):
        super().__init__(manager, **data)
        self._likes = Likes(self.manager.session, conversation_id,
                            message_id=self.id)
        self.created_at = datetime.fromtimestamp(self.created_at)

        attachments = self.data.get('attachments') or []
        self.attachments = Attachment.from_bulk_data(self.manager, attachments)

    def __repr__(self):
        klass = self.__class__.__name__
        text = self.text
        if text and len(text) > self.preview_length:
            text = text[:self.preview_length - 3] + '...'
        return ('<{}(name={!r}, text={!r}, attachments={})>'
                .format(klass, self.name, text, len(self.attachments)))

    def like(self):
        return self._likes.like()

    def unlike(self):
        return self._likes.unlike()


class Message(GenericMessage):
    def __init__(self, manager, **data):
        conversation_id = data['group_id']
        super().__init__(manager, conversation_id, **data)


class DirectMessage(GenericMessage):
    # manager could be from a chat or from a group... is that a problem?
    def __init__(self, manager, **data):
        DirectMessage.ensure_conversation_id(data)
        super().__init__(manager, **data)

    @staticmethod
    def ensure_conversation_id(data):
        # tricky tricky! the API response for *creating* a direct message
        # doesn't contain the conversation id (facepalm) so we create it
        # if it's not in the data
        if 'conversation_id' not in data:
            participant_ids = data['recipient_id'], data['sender_id']
            data['conversation_id'] = '+'.join(sorted(participant_ids))


class AttachmentMeta(type):
    _types = {}

    def __init__(cls, name, bases, attrs):
        cls._types[name.lower()] = cls


class Attachment(base.Resource, metaclass=AttachmentMeta):
    def __init__(self, manager, type, **data):
        super().__init__(manager, type=type, **data)

    def to_json(self):
        return self.data

    @classmethod
    def from_data(cls, manager, **data):
        return cls._types.get(data['type'], cls)(manager, **data)

    @classmethod
    def from_bulk_data(cls, manager, attachments):
        return [cls.from_data(manager, **a) for a in attachments]


class Image(Attachment):
    def download(self):
        return self.manager.session.get(self.url)


class Location(Attachment):
    pass


class Split(Attachment):
    pass


class Emoji(Attachment):
    pass


class Mentions(Attachment):
    pass


class Leaderboard(base.Manager):
    def __init__(self, session, group_id):
        path = 'groups/{}/likes'.format(group_id)
        super().__init__(session, path=path)

    def _get_messages(self, path=None, **params):
        url = utils.urljoin(self.url, path)
        response = self.session.get(url, params=params)
        messages = response.data['messages']
        return [Message(self, **message) for message in messages]

    def list(self, period):
        return self._get_messages(period=period)

    def list_day(self):
        return self._get_messages(period='day')

    def list_week(self):
        return self._get_messages(period='week')

    def list_month(self):
        return self._get_messages(period='month')

    def list_mine(self):
        return self._get_messages(path='mine')

    def list_for_me(self):
        return self._get_messages(path='for_me')


class Likes(base.Manager):
    def __init__(self, session, conversation_id, message_id):
        path = 'messages/{}/{}'.format(conversation_id, message_id)
        super().__init__(session, path=path)

    def like(self):
        url = utils.urljoin(self.url, 'like')
        response = self.session.post(url)
        return response.ok

    def unlike(self):
        url = utils.urljoin(self.url, 'unlike')
        response = self.session.post(url)
        return response.ok
