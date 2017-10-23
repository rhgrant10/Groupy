import time
import uuid

from .resources import Group
from .resources import Bot
from .resources import Message
from .resources import Chat
from .resources import DirectMessage
from .resources import Block
from .resources import MembershipRequest
from . import exceptions
from . import pagers
from . import utils


class Manager:
    base_url = 'https://api.groupme.com/v3/'

    def __init__(self, session, path=None):
        self.session = session
        self.url = utils.urljoin(self.base_url, path)


class Images(Manager):
    base_url = 'https://image.groupme.com/'

    def upload(self, fp):
        url = utils.urljoin(self.url, 'pictures')
        response = self.session.post(url, files={'file': fp})
        image_urls = response.data['payload']
        return image_urls

    def download(self, url):
        response = self.session.get(url)
        return response.content


class Bots(Manager):
    def __init__(self, session):
        super().__init__(session, path='bots')

    def list(self, **params):
        response = self.session.get(self.url, params=params)
        return [Bot(self, **bot) for bot in response.data]

    def create(self, name, group_id, **details):
        payload = dict(details, name=name, group_id=group_id)
        response = self.session.post(self.url, json=payload)
        return Bot(self, **response.data)

    def post(self, bot_id, text, attachments=None):
        url = utils.urljoin(self.url, 'post')
        payload = {
            'bot_id': bot_id,
            'text': text,
        }
        if attachments:
            payload['attachments'] = [a.to_json() for a in attachments]

        response = self.session.post(url, json=payload)
        return response.ok

    def destroy(self, id):
        path = '{}/destroy'.format(id)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return response.ok


class Groups(Manager):
    def __init__(self, session):
        super().__init__(session, path='groups')

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        return [Group(self, **group) for group in response.data]

    def list(self, **params):
        return pagers.GroupList(self, **params)

    def former(self, **params):
        url = utils.urljoin(self.url, 'former')
        response = self.session.get(url, params=params)
        return [Group(self, **group) for group in response.data]

    def get(self, id):
        url = utils.urljoin(self.url, id)
        response = self.session.get(url)
        return Group(self, **response.data)

    def create(self, name, **details):
        payload = dict(details, name=name)
        response = self.session.post(self.url, json=payload)
        return Group(self, **response.data)

    def update(self, id, **details):
        url = utils.urljoin(self.url, id)
        response = self.session.post(url, json=details)
        return Group(self, **response.data)

    def destroy(self, id):
        path = '{}/destroy'.format(id)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return response.ok

    def join(self, group_id, share_token):
        path = '{}/join/{}'.format(group_id, share_token)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return Group(self, **response.data)

    def rejoin(self, group_id):
        url = utils.urljoin(self.url, group_id)
        payload = {'group_id': group_id}
        response = self.session.post(url, json=payload)
        return Group(self, **response.data)


class Chats(Manager):
    def __init__(self, session):
        super().__init__(session, 'chats')

    def list(self, **params):
        response = self.session.get(self.url, params=params)
        return [Chat(self, **chat) for chat in response.data]


class Messages(Manager):
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


class DirectMessages(Manager):
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


class User(Manager):
    def __init__(self, session):
        super().__init__(session, 'users')
        self._me = None
        self._blocks = None
        self.sms_mode = SmsMode(self.session)

    @property
    def blocks(self):
        if self._blocks is None:
            self._blocks = Blocks(self.session, self.me['id'])
        return self._blocks

    @property
    def me(self):
        if self._me is None:
            self._me = self.get_me()
        return self._me

    def get_me(self):
        url = utils.urljoin(self.url, 'me')
        response = self.session.get(url)
        return response.data

    def update(self, **params):
        url = utils.urljoin(self.url, 'update')
        response = self.session.post(url, json=params)
        return response.data


class SmsMode(Manager):
    def __init__(self, session):
        super().__init__(session, 'users/sms_mode')

    def enable(self, duration, registration_id=None):
        payload = {'duration': duration}
        if registration_id is not None:
            payload['registration_id'] = registration_id
        response = self.session.post(self.url, json=payload)
        return response.ok

    def disable(self):
        url = utils.urljoin(self.url, 'delete')
        response = self.session.post(url)
        return response.ok


class Blocks(Manager):
    def __init__(self, session, user_id):
        super().__init__(session, 'blocks')
        self.user_id = user_id

    def list(self):
        params = {'user': self.user_id}
        response = self.session.get(self.url, params=params)
        blocks = response.data['blocks']
        return [Block(self, **block) for block in blocks]

    def between(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.get(self.url, params=params)
        return response.data['between']

    def block(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.post(self.url, params=params)
        block = response.data['block']
        return Block(self, **block)

    def unblock(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.delete(self.url, params=params)
        return response.ok


class Leaderboard(Manager):
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


class Likes(Manager):
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


class Memberships(Manager):

    def __init__(self, session, group_id):
        path = 'groups/{}/members'.format(group_id)
        super().__init__(session, path=path)

    def add(self, *members):
        guid = uuid.uuid4()
        for i, member in enumerate(members):
            member['guid'] = '{}-{}'.format(guid, i)

        payload = {'members': members}
        url = utils.urljoin(self.url, 'add')
        response = self.session.post(url, json=payload)
        return MembershipRequest(self, *members, **response.data)

    def check(self, results_id):
        path = 'results/{}'.format(results_id)
        url = utils.urljoin(self.url, path)
        response = self.session.get(url)
        if response.status_code == 503:
            raise exceptions.ResultsNotReady(response)
        if response.status_code == 404:
            raise exceptions.ResultsExpired(response)
        return response.data['members']

    def remove(self, membership_id):
        path = '{}/remove'.format(membership_id)
        url = utils.urljoin(self.url, path)
        payload = {'membership_id': membership_id}
        response = self.session.post(url, json=payload)
        return response.ok
