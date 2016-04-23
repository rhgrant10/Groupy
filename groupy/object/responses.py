"""
.. module:: responses
    :platform: Unix, Windows
    :synopsis: A module containing all response classes

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

This module contains classes that encapsulate the information returned in API
responses.

"""
import textwrap
import time

from datetime import datetime
from collections import Counter

from .. import config
from ..api import status
from ..api import errors
from ..api import endpoint
from .listers import FilterList, MessagePager
from .attachments import AttachmentFactory


__all__ = ['Recipient', 'Group', 'Member', 'Message', 'Bot', 'User']


class ApiResponse(object):
    """Base class for all API responses.

    .. note::

        All keyword arguments become properties.

    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Recipient(ApiResponse):
    """Base class for Group and Member.

    Recipients can post and receive messages.

    :param endpoint: the API endpoint for messages
    :type endpoint: :class:`~groupy.api.endpoint.Endpoint`
    :param str mkey: the :class:`dict` key under which the endpoint returns
        messages
    :param str idkey: the :class:`dict` key whose value represents the key for
        posting and retrieving messages
    """
    def __init__(self, endpoint, mkey, idkey, **kwargs):
        self._endpoint = endpoint
        self._mkey = mkey
        self._idkey = kwargs.get(idkey)
        self.message_count = kwargs.pop('count', 0)
        super().__init__(**kwargs)

    # Splits text into chunks so that each is less than the chunk_size.
    @staticmethod
    def _chunkify(text, chunk_size=1000):
        if not text:
            return [None]
        return textwrap.wrap(text, chunk_size)

    def __len__(self):
        """Return the number of messages in the recipient.
        """
        return self.message_count

    def post(self, text, *attachments):
        """Post a message to the recipient.

        Although the API limits messages to 1000 characters, this method will
        split the text component into as many as necessary and include the
        attachments in the final message. Note that a list of messages sent is
        always returned, even if it contains only one element.

        :param str text: the message text
        :param list attachments: the attachments to include
        :returns: a list of raw API responses (sorry!)
        :rtype: :class:`list`
        """
        if not text and not attachments:
            raise ValueError('must be one attachment or text')
        *chunks, last = self._chunkify(text)
        sent = []
        for chunk in chunks:
            sent.append(self._endpoint.create(self._idkey, chunk))
        sent.append(self._endpoint.create(self._idkey, last, *attachments))
        return sent

    def messages(self, before=None, since=None, after=None, limit=None):
        """Return a page of messages from the recipient.

        .. note::

            Only one of ``before``, ``after``, or ``since`` can be specified in
            a single call.

        :param str before: a reference message ID
        :param str since: a reference message ID
        :param str after: a reference message ID
        :param int limit: maximum number of messages to include in the page
        :returns: a page of messages
        :rtype: :class:`~groupy.object.listers.MessagePager`
        :raises ValueError: if more than one of ``before``, ``after`` or
            ``since`` are specified
        """
        # Check arguments.
        not_None_args = []
        for arg in (before, since, after):
            if arg is not None:
                not_None_args.append(arg)
        if len(not_None_args) > 1:
            raise ValueError("Only one of 'after', 'since', and 'before' can "
                             "be specified in a single call")

        # Messages obtained with the 'after' parameter are in reversed order.
        backward = after is not None
        # Fetch the messages.
        try:
            r = self._endpoint.index(self._idkey, before_id=before,
                                     since_id=since, after_id=after)
        except errors.ApiError as e:
            # NOT_MODIFIED, in this case, means no more messages. Some versions
            # of the API return the 304 code inside the response envelope, but
            # sometimes there is no JSON response and it returns the 304 in the
            # response http code only.
            try:
                if e.args[0]['code'] == status.NOT_MODIFIED:
                    return None
            except TypeError:
                if e.args[0].status_code == status.NOT_MODIFIED:
                    return None
            raise e
        # Update the message count and grab the messages.
        self.message_count = r['count']
        messages = (Message(self, **m) for m in r[self._mkey])
        return MessagePager(self, messages, backward=backward)


class Group(Recipient):
    """A GroupMe group.
    """
    def __init__(self, **kwargs):
        messages = kwargs.pop('messages', {})
        members = kwargs.pop('members')
        super().__init__(endpoint.Messages, 'messages', 'id', **kwargs)

        self.id = kwargs.get('id')
        self.group_id = kwargs.get('group_id')
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.image_url = kwargs.get('image_url')
        self.creator_user_id = kwargs.get('creator_user_id')
        self.created_at = datetime.fromtimestamp(kwargs.get('created_at'))
        self.updated_at = datetime.fromtimestamp(kwargs.get('updated_at'))
        ca = messages.get('last_message_created_at')
        if ca is not None and ca >= 0:
            self.last_message_created_at = datetime.fromtimestamp(ca)
            self.last_message_id = messages.get('last_message_id')
        else:
            self.last_message_created_at = None
            self.last_message_id = None
        self.message_count = messages.get('count')
        self._members = [Member(**m) for m in members]
        self.share_url = kwargs.get('share_url')

        # Undocumented properties.
        # 'max_members' for groups, 'max_memberships' for former groups.
        for k in ['max_members', 'max_memberships']:
            if k in kwargs:
                self.max_members = kwargs[k]
                break
        else:
            self.max_members = None
        self.office_mode = kwargs.get('office_mode')
        self.phone_number = kwargs.get('phone_number')

    def __repr__(self):
        return "{}, {}/{} members, {} messages".format(
            self.name, len(self.members()),
            self.max_members, self.message_count)

    @classmethod
    def list(cls, former=False):
        """List all of your current or former groups.

        :param bool former: ``True`` if former groups should be listed,
            ``False`` (default) lists current groups
        :returns: a list of groups
        :rtype: :class:`~groupy.object.listers.FilterList`
        """
        # Former groups come as a single page.
        if former:
            groups = endpoint.Groups.index(former=True)
            return FilterList(Group(**g) for g in groups)
        # Current groups are listed in pages.
        page = 1
        groups = []
        next_groups = endpoint.Groups.index(page=page)
        while next_groups:
            groups.extend(next_groups)
            page += 1
            try:
                next_groups = endpoint.Groups.index(page=page)
            except errors.ApiError:
                next_groups = None
        return FilterList(Group(**g) for g in groups)

    @classmethod
    def create(cls, name, description=None, image_url=None, share=True):
        """Create a new group.

        :param str name: the group name
        :param str description: the group description
        :param str image_url: the GroupMe image service URL for a group avatar
        :param bool share: whether to generate a join link
        :returns: the newly created group
        :rtype: :class:`~groupy.object.responses.Group`
        """
        return cls(**endpoint.Groups.create(name=name, description=description,
                                            image_url=image_url, share=share))

    def destroy(self):
        """Disband (destroy) a group that you created.

        If unsuccessful, this raises an :exc:`~groupy.api.errors.ApiError`

        :returns: :data:`~groupy.api.status.OK`
        """
        try:
            endpoint.Groups.destroy(self.group_id)
        except errors.ApiError as e:
            if e.args[0]['code'] != status.OK:
                raise
            return e.args[0]['code']
        return True

    def refresh(self):
        """Refresh the group information from the API.
        """
        self.__init__(**endpoint.Groups.show(self.id))

    def update(self, name=None, description=None, image_url=None, share=None):
        """Change group information.

        :param str name: the new name of the group
        :param str description: the new description of the group
        :param str image_url: the URL for the new group image
        :param bool share: whether to generate a share URL
        """
        endpoint.Groups.update(self.group_id,
                               name=name, description=description,
                               image_url=image_url, share=share)
        self.refresh()

    def members(self):
        """Return a list of the members in the group.

        :returns: the members of the group
        :rtype: :class:`~groupy.object.listers.FilterList`
        """
        return FilterList(self._members)

    def add(self, *members, refresh=False):
        """Add a member to a group.

        Each member can be either an instance of
        :class:`~groupy.object.responses.Member` or a :class:`dict` containing
        ``nickname`` and one of ``email``, ``phone_number``, or ``user_id``.

        :param list members: members to add to the group
        :param bool refresh: ``True`` if the group information should be
            automatically refreshed from the API, ``False`` by default
        :returns: the results ID of the add call
        :rtype: str
        """
        ids = (Member.identify(m) for m in members)
        r = endpoint.Members.add(self.id, *ids)
        if refresh:
            self.refresh()
        return r['results_id']

    def remove(self, member, refresh=False):
        """Remove a member from the group.

        .. note::

            The group must contain the member to be removed. This will *not* be
            the case if the group information has not been requested since the
            member was *added*. When in doubt, use the
            :func:`~groupy.object.responses.Group.refresh` method to update the
            internal list of members before attempting to remove them.

        :param member: the member to remove
        :param bool refresh: ``True`` if the group information should be
            automatically refreshed from the API, ``False`` by default
        :type member: :class:`~groupy.object.responses.Member`
        :returns: ``True`` if successful
        :rtype: bool
        :raises groupy.api.errors.ApiError: if removal is not successful
        """
        # Use the member from this group because they have the correct id.
        gmember = self.members().filter(user_id=member.user_id).first
        if not gmember or not gmember.id:
            return False
        try:
            endpoint.Members.remove(self.id, gmember.id)
        except errors.ApiError as e:
            if e.args[0]['code'] != status.OK:
                raise
        if refresh:
            self.refresh()
        return True


class Member(Recipient):
    """A GroupMe member.
    """
    def __init__(self, **kwargs):
        super().__init__(endpoint.DirectMessages, 'direct_messages',
                         'user_id', **kwargs)
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.nickname = kwargs.get('nickname')
        self.muted = kwargs.get('muted')
        self.image_url = kwargs.get('image_url')
        self.autokicked = kwargs.get('autokicked')
        self.app_installed = kwargs.get('app_installed')
        self.guid = kwargs.get('guid', None)
        self.message_count = None

    @classmethod
    def list(cls):
        """List all known members regardless of group membership.

        :returns: a list of all known members
        :rtype: :class:`~groupy.objects.FilterList`
        """
        groups = Group.list()
        members = {}
        for g in groups:
            for m in g.members():
                if m.user_id not in members:
                    members[m.user_id] = {
                        'member': m,
                        'name': Counter({m.nickname: 1})
                    }
                else:
                    members[m.user_id]['name'][m.nickname] += 1
        renamed = []
        for d in members.values():
            d['member'].nickname = d['name'].most_common()[0][0]
            renamed.append(d['member'])
        return FilterList(renamed)

    def __repr__(self):
        return self.nickname

    def __bool__(self):
        return True

    @property
    def guid(self):
        if not self._guid:
            self._guid = self._next_guid()
        return self._guid

    @guid.setter
    def guid(self, value):
        self._guid = value

    # Create and return a new guid based on the current time.
    @staticmethod
    def _next_guid():
        return str(time.time())

    def identification(self):
        """Return the identification of the member.

        A member is identified by their ``nickname`` and ``user_id``
        properties. If the member does not yet have a GUID, a new one is
        created and assigned to them (and is returned alongside the
        ``nickname`` and ``user_id`` properties).

        :returns: the ``nickname``, ``user_id``, and ``guid`` of the member
        :rtype: :class:`dict`
        """
        return {
            'nickname': self.nickname,
            'user_id': self.user_id,
            'guid': self.guid         # new guid set if nonexistant
        }

    @classmethod
    def identify(cls, member):
        """Return or create an identification for a member.

        Member identification is required for adding them to groups. If member
        is a :class:`dict`, it must contain the following keys:

        - ``nickname``
        - ``user_id`` or ``email`` or ``phone_number``

        If an identification cannot be created then raise an
        :exc:`ValueError`.

        :param member: either a :class:`~groupy.object.responses.Member` or a
            :class:`dict` with the required keys
        :returns: the identification of member
        :rtype: :class:`dict`
        :raises ValueError: if an identification cannot be made
        """
        if isinstance(member, cls):
            return member.identification()
        elif isinstance(member, dict):
            m = Member(**member)
            return m.identification()
        raise ValueError('no identification could be made')


class Message(ApiResponse):
    """A GroupMe message.

    :param recipient: the reciever of the message
    :type recipient: :class:`~groupy.object.responses.Recipient`
    """
    _user = None

    def __init__(self, recipient, **kwargs):
        super().__init__()
        self._recipient = recipient

        self.id = kwargs.get('id')
        self.source_guid = kwargs.get('source_guid')
        self.created_at = datetime.fromtimestamp(kwargs.get('created_at'))
        self.user_id = kwargs.get('user_id')
        self.group_id = kwargs.get('group_id')
        self.recipient_id = kwargs.get('recipient_id')
        self.name = kwargs.get('name')
        self.avatar_url = kwargs.get('avatar_url')
        self.text = kwargs.get('text')
        self.system = kwargs.pop('system', False)
        self.favorited_by = kwargs.get('favorited_by')
        self.attachments = [
            AttachmentFactory.create(**a) for a in kwargs.get('attachments')]

        # Determine the conversation id (different for direct messages)
        try:    # assume group message
            self._conversation_id = recipient.group_id
        except AttributeError:  # oops, its a direct message
            if self._user is None:
                self._user = User.get()
            participants = [self._user.user_id, recipient.user_id]
            self._conversation_id = '+'.join(sorted(participants))

    @property
    def recipient(self):
        """Return the source of the message.

        If the message is a direct message, this returns a member. Otherwise,
        it returns a group.

        :returns: the source of the message
        :rtype: :class:`~groupy.object.responses.Recipient`
        """
        return self._recipient

    def __repr__(self):
        msg = "{}: {}".format(self.name, self.text or "")
        if self.attachments:
            for a in self.attachments:
                msg += " +<{}>".format(str(a))
        return msg

    def __len__(self):
        """Return the length of the message text.
        """
        return len(self.text) if self.text else 0

    def like(self):
        """Like the message.

        :returns: ``True`` if successful
        :rtype: bool
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Likes.create(self._conversation_id, self.id)
        except errors.ApiError as e:
            if e.args[0]['code'] != status.OK:
                raise
            return e.args[0]['code']
        return True

    def unlike(self):
        """Unlike the message.

        :returns: ``True`` if successful
        :rtype: bool
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Likes.destroy(self._conversation_id, self.id)
        except errors.ApiError as e:
            if e.args[0]['code'] != status.OK:
                raise
            return e.args[0]['code']
        return True

    def likes(self):
        """Return a :class:`~groupy.object.listers.FilterList` of the
        members that like the message.

        :returns: a list of the members who "liked" this message
        :rtype: :class:`~groupy.object.listers.FilterList`
        """
        try:
            liked = filter(
                lambda m: m.user_id in self.favorited_by,
                self._recipient.members())
        except AttributeError:
            liked = []
            for i in self.favorited_by:
                if i == self._user.user_id:
                    liked.append(self._user)
                elif i == self.recipient_id:
                    liked.append(self._recipient)
        return FilterList(liked)

    def is_from_me(self):
        """Return ``True`` if the message was sent by you.

        :rtype: bool
        """
        return self.user_id == self._user.user_id

    def is_liked_by_me(self):
        """Return ``True`` if the message was liked by you.

        :rtype: bool
        """
        return self._user.user_id in self.favorited_by

    def metions_me(self):
        """Return ``True`` if the message "@" mentions you.

        :rtype: bool
        """
        for a in self.attachments:
            if a.type == 'mentions' and self._user.user_id in a.user_ids:
                return True
        return False


class Bot(ApiResponse):
    """A GroupMe bot.

    Each bot belongs to a single group. Messages posted by the bot are always
    posted to the group to which the bot belongs.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.bot_id = kwargs.get('bot_id')
        self.group_id = kwargs.get('group_id')
        self.name = kwargs.get('name')
        self.avatar_url = kwargs.get('avatar_url')
        self.callback_url = kwargs.get('callback_url')

    def __repr__(self):
        return self.name

    @classmethod
    def create(cls, name, group, avatar_url=None, callback_url=None):
        """Create a new bot.

        :param str name: the name of the bot
        :param group: the group to which the bot will belong
        :type group: :class:`~groupy.object.responses.Group`
        :param str avatar_url: the URL for a GroupMe image to be used as the
            bot's avatar
        :param str callback_url: the URL to which each group message will be
            POSTed
        :returns: the new bot
        :rtype: :class:`~groupy.object.responses.Bot`
        """
        bot = endpoint.Bots.create(name, group.group_id,
                                   avatar_url, callback_url)
        return cls(**bot['bot'])

    @classmethod
    def list(cls):
        """Return a list of your bots.

        :returns: a list of your bots
        :rtype: :class:`~groupy.object.listers.FilterList`
        """
        return FilterList(Bot(**b) for b in endpoint.Bots.index())

    def post(self, text, picture_url=None):
        """Post a message to the group of the bot.

        :param str text: the message text
        :param str picture_url: the GroupMe image URL for an image
        :returns: ``True`` if successful
        :rtype: bool
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Bots.post(self.bot_id, text, picture_url)
        except errors.ApiError as e:
            if e.args[0].status_code >= status.BAD_REQUEST:
                raise
        return True

    def destroy(self):
        """Destroy the bot.

        :returns: ``True`` if successful
        :rtype: bool
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Bots.destroy(self.bot_id)
        except errors.ApiError as e:
            if e.args[0].status_code != status.OK:
                raise
        return True


class User(ApiResponse):
    """A GroupMe user.

    This is you, as determined by your API key.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.created_at = datetime.fromtimestamp(kwargs.get('created_at'))
        self.udpated_at = datetime.fromtimestamp(kwargs.get('updated_at'))
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.phone_number = kwargs.get('phone_number')
        self.image_url = kwargs.get('image_url')
        self.sms = kwargs.get('sms')

    def __repr__(self):
        return self.name

    @property
    def nickname(self):
        """Your user name.
        """
        return self.name

    @classmethod
    def get(cls):
        """Return your user information.

        :returns: your user information
        :rtype: :class:`dict`
        """
        return cls(**endpoint.Users.me())

    @classmethod
    def enable_sms(cls, duration=4, registration_token=None):
        """Enable SMS mode.

        Each client has a unique registration token that allows it to recieve
        push notifications. Enabling SMS mode causes GroupMe to suppress those
        push notification and send SMS text messages instead for a number of
        hours no greater than 48.

        .. note::

            If the ``registration_token`` is omitted, no push notifications
            will be suppressed and the user will recieve *both* text messages
            *and* push notifications.

        :param int duration: the number of hours for which to send text
            messages
        :param str registration_token: the push notification token for which
            messages should be suppressed
        :returns: ``True`` if successful
        :rtype: :obj:`bool`
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Sms.create(duration, registration_token)
        except errors.ApiError as e:
            if e.args[0]['code'] != status.CREATED:
                raise
            return e.args[0]['code']
        return True

    @classmethod
    def disable_sms(cls):
        """Disable SMS mode.

        Disabling SMS mode causes push notifications to resume and SMS text
        messages to be discontinued.

        :returns: ``True`` if successful
        :rtype: :obj:`bool`
        :raises groupy.api.errors.ApiError: if unsuccessful
        """
        try:
            endpoint.Sms.delete()
        except errors.ApiError as e:
            if e.args[0]['code'] != status.OK:
                raise
            return e.args[0]['code']
        return True
