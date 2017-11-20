import time
from datetime import datetime

from . import base
from .attachments import Attachment
from groupy import utils
from groupy import pagers


class Messages(base.Manager):
    """A message manager for a particular group.

    :param session: the request session
    :type session: :class:`~groupy.session.Session`
    :param str group_id: the group_id of a group
    """

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
        """Return a page of messages from the group.

        :param kwargs params: optional listing parameters
        :return: messages from the group
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return pagers.MessageList(self, self._raw_list, **params)

    def list_before(self, message_id, **params):
        """Return a page of messages from the group created before a message.

        This is used to page backwards through messages.

        :param str message_id: the ID of a message
        :param kwargs params: optional listing parameters
        :return: messages from the group
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(before_id=message_id, **params)

    def list_since(self, message_id, **params):
        """Return a page of messages from the group created since a message.

        This is used to fetch the most recent messages after another. There
        may exist messages between the one given and the ones returned. Use
        :func:`list_after` to retrieve newer messages without skipping any.

        :param str message_id: the ID of a message
        :param kwargs params: optional listing parameters
        :return: messages from the group
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(since_id=message_id, **params)

    def list_after(self, message_id, **params):
        """Return a page of messages from the group created after a message.

        This is used to page forwards through messages.

        :param str message_id: the ID of a message
        :param kwargs params: optional listing parameters
        :return: messages from the group
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(after_id=message_id, **params)

    def create(self, text=None, attachments=None, source_guid=None):
        """Create a new message in the group.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :param str source_guid: a unique identifier for the message
        :return: the created message
        :rtype: :class:`~groupy.api.messages.Message`
        """
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
        if response.status_code == 304:
            return []
        messages = response.data['direct_messages']
        return [DirectMessage(self, **message) for message in messages]

    def list(self, **params):
        return pagers.MessageList(self, self._raw_list, **params)

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
            message['attachments'] = [a.to_json() for a in attachments]

        payload = {'direct_message': message}
        response = self.session.post(self.url, json=payload)
        message = response.data['direct_message']
        return DirectMessage(self, **message)


class GenericMessage(base.ManagedResource):
    preview_length = 42

    def __init__(self, manager, conversation_id, **data):
        super().__init__(manager, **data)
        self.conversation_id = conversation_id
        self.created_at = datetime.fromtimestamp(self.created_at)
        attachments = self.data.get('attachments') or []
        try:
            self.attachments = Attachment.from_bulk_data(attachments)
        except Exception:
            print(attachments)
            import sys
            sys.exit(1)

        self._likes = Likes(self.manager.session, self.conversation_id,
                            message_id=self.id)

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
        data['conversation_id'] = self.__class__.get_conversation_id(data)
        super().__init__(manager, **data)

    @staticmethod
    def get_conversation_id(data):
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            participant_ids = data['recipient_id'], data['sender_id']
            conversation_id = '+'.join(sorted(participant_ids))
        return conversation_id


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


class Gallery(base.Manager):
    def __init__(self, session, group_id):
        path = 'conversations/{}/gallery'.format(group_id)
        super().__init__(session, path=path)

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        messages = response.data['messages']
        return [Message(self, **message) for message in messages]

    def list(self, **params):
        return pagers.MessageList(self, self._raw_list, **params)

    def list_before(self, message_id, **params):
        return self.list(before_id=message_id, **params)

    def list_since(self, message_id, **params):
        return self.list(since_id=message_id, **params)

    def list_after(self, message_id, **params):
        return self.list(after_id=message_id, **params)
