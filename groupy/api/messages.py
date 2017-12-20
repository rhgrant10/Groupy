import time
from datetime import datetime, timedelta

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

    def list(self, before_id=None, since_id=None, after_id=None, limit=20):
        """Return a page of group messages.

        The messages come in reversed order (newest first). Note you can only
        provide _one_ of ``before_id``, ``since_id``, or ``after_id``.

        :param str before_id: message ID for paging backwards
        :param str after_id: message ID for paging forwards
        :param str since_id: message ID for most recent messages since
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return pagers.MessageList(self, self._raw_list, before_id=before_id,
                                  after_id=after_id, since_id=since_id,
                                  limit=limit)

    def list_before(self, message_id, limit=None):
        """Return a page of group messages created before a message.

        This can be used to page backwards through messages.

        :param str message_id: the ID of a message
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(before_id=message_id, limit=None)

    def list_since(self, message_id, limit=None):
        """Return a page of group messages created since a message.

        This is used to fetch the most recent messages after another. There
        may exist messages between the one given and the ones returned. Use
        :func:`list_after` to retrieve newer messages without skipping any.

        :param str message_id: the ID of a message
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(since_id=message_id, limit=limit)

    def list_after(self, message_id, limit=None):
        """Return a page of group messages created after a message.

        This is used to page forwards through messages.

        :param str message_id: the ID of a message
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(after_id=message_id, limit=limit)

    def list_all(self, limit=None):
        """Return all group messages.

        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list().autopage()

    def list_all_before(self, message_id, limit=None):
        """Return all group messages created before a message.

        :param str message_id: the ID of a message
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list_before(message_id, limit=limit).autopage()

    def list_all_after(self, message_id, limit=None):
        """Return all group messages created after a message.

        :param str message_id: the ID of a message
        :param int limit: maximum number of messages per page
        :return: group messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list_after(message_id, limit=limit).autopage()

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
    """Manager for direct messages with a particular user.

    :param session: request session
    :param str other_user_id: user_id of another user
    """

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

    def list(self, before_id=None, since_id=None, **kwargs):
        """Return a page of direct messages.

        The messages come in reversed order (newest first). Note you can only
        provide _one_ of ``before_id``, ``since_id``.

        :param str before_id: message ID for paging backwards
        :param str since_id: message ID for most recent messages since
        :return: direct messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return pagers.MessageList(self, self._raw_list, before_id=before_id,
                                  since_id=since_id, **kwargs)

    def list_before(self, message_id, **kwargs):
        """Return a page of direct messages created before a message.

        This can be used to page backwards through messages.

        :param str message_id: the ID of a message
        :return: direct messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(before_id=message_id, **kwargs)

    def list_since(self, message_id, **kwargs):
        """Return a page of direct messages created since a message.

        This is used to fetch the most recent messages after another. There
        may exist messages between the one given and the ones returned.

        :param str message_id: the ID of a message
        :return: direct messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(since_id=message_id, **kwargs)

    def list_all(self, before_id=None, since_id=None, **kwargs):
        """Return all direct messages.

        The messages come in reversed order (newest first). Note you can only
        provide _one_ of ``before_id``, ``since_id``.

        :param str before_id: message ID for paging backwards
        :param str since_id: message ID for most recent messages since
        :return: direct messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list(before_id=before_id, since_id=since_id, **kwargs).autopage()

    def list_all_before(self, message_id, **kwargs):
        """Return all direct messages created before a message.

        This can be used to page backwards through messages.

        :param str message_id: the ID of a message
        :return: direct messages
        :rtype: :class:`~groupy.pagers.MessageList`
        """
        return self.list_before(message_id, **kwargs).autopage()

    def create(self, text=None, attachments=None, source_guid=None):
        """Send a new direct message to the user.

        Only provide the source_guid if you want to control it.

        :param str text: the message content
        :param attachments: message attachments
        :param str source_guid: a client-side unique ID for the message
        :return: the message sent
        :rtype: :class:`~groupy.api.messages.DirectMessage`
        """
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
    """A message.

    :param manager: a message manager
    :param str conversation_id: the ID for the conversation
    :param kwargs data: the data of the message
    """

    #: number of characters seen in the repr output
    preview_length = 42

    def __init__(self, manager, conversation_id, **data):
        super().__init__(manager, **data)
        self.conversation_id = conversation_id
        self.created_at = utils.get_datetime(self.data['created_at'])
        attachments = self.data.get('attachments') or []
        self.attachments = Attachment.from_bulk_data(attachments)
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
        """Like the message."""
        return self._likes.like()

    def unlike(self):
        """Unlike the message."""
        return self._likes.unlike()


class Message(GenericMessage):
    """A group message."""

    def __init__(self, manager, **data):
        conversation_id = data['group_id']
        super().__init__(manager, conversation_id, **data)


class DirectMessage(GenericMessage):
    """A direct message between two users."""

    # manager could be from a chat or from a group... is that a problem?
    def __init__(self, manager, **data):
        data['conversation_id'] = self.__class__.get_conversation_id(data)
        super().__init__(manager, **data)

    @staticmethod
    def get_conversation_id(data):
        # some endpoints return direct messages with a conversation id. if not,
        # we have to construct it
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            participant_ids = data['recipient_id'], data['sender_id']
            conversation_id = '+'.join(sorted(participant_ids))
        return conversation_id


class Leaderboard(base.Manager):
    """Manager for messages on the leaderboard."""

    def __init__(self, session, group_id):
        path = 'groups/{}/likes'.format(group_id)
        super().__init__(session, path=path)

    def _get_messages(self, path=None, **params):
        url = utils.urljoin(self.url, path)
        response = self.session.get(url, params=params)
        messages = response.data['messages']
        return [Message(self, **message) for message in messages]

    def list(self, period):
        """List most liked messages for a given period.

        :param str period: either "day", "week", or "month"
        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(period=period)

    def list_day(self):
        """List most liked messages for the last day.

        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(period='day')

    def list_week(self):
        """List most liked messages for the last week.

        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(period='week')

    def list_month(self):
        """List most liked messages for the last month.

        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(period='month')

    def list_mine(self):
        """List messages you liked.

        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(path='mine')

    def list_for_me(self):
        """List your top liked messages.

        :return: the messages
        :rtype: :class:`list`
        """
        return self._get_messages(path='for_me')


class Likes(base.Manager):
    """Manager for likes/unlikes of a particular message.

    The message can be from either a group or a chat.

    :param session: request session
    :param str conversation_id: unique ID for a the conversation from which
                                the message originates
    :param str message_id: unique ID of the message to like/unlike
    """

    def __init__(self, session, conversation_id, message_id):
        path = 'messages/{}/{}'.format(conversation_id, message_id)
        super().__init__(session, path=path)

    def like(self):
        """Like the message."""
        url = utils.urljoin(self.url, 'like')
        response = self.session.post(url)
        return response.ok

    def unlike(self):
        """Unlike the message."""
        url = utils.urljoin(self.url, 'unlike')
        response = self.session.post(url)
        return response.ok


class Gallery(base.Manager):
    """Manager for messages in the gallery.

    This endpoint is undocumented!

    :param session: request session
    :param str group_id: group_id for a particular group
    """

    def __init__(self, session, group_id):
        path = 'conversations/{}/gallery'.format(group_id)
        super().__init__(session, path=path)

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        messages = response.data['messages']
        return [Message(self, **message) for message in messages]

    def _convert_to_rfc3339(self, when=None):
        if when is None:
            return None
        return utils.get_rfc3339(when)

    def list(self, before=None, since=None, after=None, limit=100):
        before = self._convert_to_rfc3339(before)
        since = self._convert_to_rfc3339(since)
        after = self._convert_to_rfc3339(after)
        return pagers.GalleryList(self, self._raw_list, before=before,
                                  since=since, after=after, limit=limit)

    def list_before(self, when, limit=100):
        return self.list(before=when, limit=limit)

    def list_since(self, when, limit=100):
        return self.list(since=when, limit=limit)

    def list_after(self, when, limit=100):
        return self.list(after=when, limit=limit)

    def list_all(self, **params):
        return self.list(**params).autopage()

    def list_all_before(self, when, limit=100):
        return self.list_before(when=when, limit=limit).autopage()

    def list_all_after(self, when, limit=100):
        return self.list_after(when=when, limit=limit).autopage()

