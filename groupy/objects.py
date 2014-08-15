"""
.. module:: objects
   :platform: Unix, Windows
   :synopsis: Module that abstracts the API calls into sensible objects.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>


"""
from . import api
from . import status
from . import errors

import operator
import time

__all__ = ['ApiResponse', 'Recipient', 'Group', 'Member', 'Message',
    'Bot', 'User', 'Attachment', 'FilterList', 'MessagePager']

class FilterList(list):
    """A filterable list.

    Acts just like a regular :class:`list`, except it can be filtered using a
    special keyword syntax. Also, the first and last items are special
    properties.
    """
    def filter(self, **kwargs):
        """Filter the list and return a new instance.

        Arguments are keyword arguments only, and can be appended with
        operator method names to indicate relationships other than equals.
        For example, to filter the list down to only items whose ``name``
        property contains "ie":

        .. code-block:: python

            new_list = filter_list.filter(name__contains='ie')

        As another example, this filters the list down to only those
        with a ``created`` property that is less than 1234567890:

        .. code-block:: python

            new_list = filter_list.filter(created__lt=1234567890)

        Acceptable operators are:

        - ``__lt``: less than
        - ``__gt``: greater than
        - ``__contains``: contains
        - ``__eq``: equal to
        - ``__ne``: not equal to
        - ``__le``: less than or equal to
        - ``__ge``: greater than or equal to

        Use of any operator listed here results in a
        :class:`InvalidOperatorError<groupy.errors.InvalidOperatorError>`.

        :return: a new list with potentially less items than the original
        :rtype: :class:`FilterList<groupy.objects.FilterList>`
        """
        kvops = []
        for k, v in kwargs.items():
            if '__' in k[1:-1]:   # don't use it if at the start or end of k
                k, o = k.rsplit('__', 1)
                try:
                    op = getattr(operator, o)
                except AttributeError:
                    raise errors.InvalidOperatorError("__{}".format(o))
            else:
                op = operator.eq
            kvops.append((k, v, op))
        test = lambda i, k, v, op: hasattr(i, k) and op(getattr(i, k), v)
        criteria = lambda i: all(test(i, k, v, op) for k, v, op in kvops)
        return FilterList(filter(criteria, self))

    @property
    def first(self):
        try:
            return self[0]
        except IndexError:
            return None

    @property
    def last(self):
        try:
            return self[-1]
        except IndexError:
            return None


class MessagePager(FilterList):
    """A filterable, extendable page of messages.

    :param group: the group from which to page through messages
    :type group: :class:`Group<groupy.objects.Group>`
    :param messages: the initial page of messages
    :type messages: :class:`list`
    :param backward: ``True`` if the oldest message is at index 0, ``False``
        otherwise
    :type backward: :obj:`bool`
    """
    def __init__(self, group, messages, backward=False):
        super().__init__(messages)
        self.backward = backward
        self.group = group

    @property
    def oldest(self):
        """Return the oldest message in the list.

        :returns: the oldest message in the list
        :rtype: :class:`Message<groupy.objects.Message>`
        """
        return self.first if self.backward else self.last

    @property
    def newest(self):
        """Return the newest message in the list.

        :returns: the newest message in the list
        :rtype: :class:`Message<groupy.objects.Message>`
        """
        return self.last if self.backward else self.first

    def prepend(self, messages):
        """Prepend a list of messages to the list.

        :param messages: the messages to prepend
        :type messages: :class:`list`
        """
        for each in messages:
            self.insert(0, each)

    def newer(self):
        """Return the next (newer) page of messages.

        :returns: a newer page of messages
        :rtype: :class:`MessagePager<groupy.objects.MessagePager>`
        """
        return self.group.messages(after=self.newest.id)

    def older(self):
        """Return the previous (older) page of messages.
        
        :returns: an older page of messages
        :rtype: :class:`MessagePager<groupy.objects.MessagePager>`
        """
        return self.group.messages(before=self.oldest.id)

    def inewer(self):
        """Add in-place the next (newer) page of messages.
        
        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        new = self.newer()
        if not new:
            return False
        if self.backward:
            self.extend(self.newer())
        else:
            self.prepend(self.newer())
        return True

    def iolder(self):
        """Add in-place the previous (older) page of messages.
        
        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        old = self.older()
        if not old:
            return False
        if self.backward:
            self.prepend(self.older())
        else:
            self.extend(self.older())
        return True


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

    Recipients can post and recieve messages.

    :param endpoint: the API endpoint for messages
    :type endpoint: :class:`Endpoint<groupy.objects.Endpoint>`
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
    def _chunkify(text, chunk_size=450):
        if text is None:
            return [None]
        chunks = []
        while len(text) > chunk_size:
            portion = text[:chunk_size]
            # Find the index of the final whitespace character.
            i = len(portion.rsplit(None, 1)[0])
            # Append the chunk up to that character.
            chunks.append(portion[:i].strip())
            # Re-assign the text to all but the appended chunk.
            text = text[i:].strip()
        chunks.append(text)
        return chunks

    def __len__(self):
        """Return the number of messages in the recipient.
        """
        return self.message_count

    def post(self, text, *attachments):
        """Post a message to the recipient.

        Although the API limits messages to 450 characters, this method will
        split the text component into as many as necessary and include the
        attachments in the final message. Note that a list of messages sent is
        always returned, even if it contains only one element.

        :param str text: the message text
        :param attachments: the attachments to include
        :type attachments: :class:`list`
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

        :param str before: a reference message ID
        :param str since: a reference message ID
        :param str after: a reference message ID
        :param int limit: maximum number of messages to include in the page
        :returns: a page of messages
        :rtype: :class:`MessagePager<groupy.objects.MessagePager>`
        """
        # Messages obtained with the 'after' parameter are in reversed order.
        backward = after is not None
        # Fetch the messages.
        try:
            r = self._endpoint.index(self._idkey, before_id=before,
                                    since_id=since, after_id=after)
        except errors.InvalidResponseError as e:
            # NOT_MODIFIED, in this case, means no more messages.
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
        super().__init__(api.Messages, 'messages', 'id', **kwargs)
        self.message_count = messages.get('count')
        self.last_message_id = messages.get('last_message_id')
        self.last_message_created_at = messages.get('last_message_created_at')
        self._members = [Member(**m) for m in members]
        for k in ['max_members', 'max_memberships']:
            if k in kwargs:
                self.max_members = kwargs[k]
        else:
            self.max_members = None

    def __repr__(self):
        return "{}, {}/{} members, {} messages".format(
            self.name, len(self.members()),
            self.max_members, self.message_count)

    @classmethod
    def list(cls, former=False):
        """List all of your current or former groups.

        :param former: ``True`` if former groups should be listed, 
            ``False`` (default) lists current groups
        :type former: :obj:`bool`
        :returns: a list of groups
        :rtype: :class:`FilterList<groupy.objects.FilterList>`
        """
        # Former groups come as a single page.
        if former:
            groups = api.Groups.index(former=True)
            return FilterList(Group(**g) for g in groups)
        # Current groups are listed in pages.
        page = 1
        groups = []
        next_groups = api.Groups.index(page=page)
        while next_groups:
            groups.extend(next_groups)
            page += 1
            try:
                next_groups = api.Groups.index(page=page)
            except errors.InvalidResponseError:
                next_groups = None
        return FilterList(Group(**g) for g in groups)

    def refresh(self):
        """Refresh the group information from the API.
        """
        self.__init__(**api.Groups.show(self.id))

    def members(self):
        """Return a list of the members in the group.

        :returns: the members of the group
        :rtype: :class:`FilterList<groupy.objects.FilterList>`
        """
        return FilterList(self._members)

    def add(self, *members):
        """Add a member to a group.

        Each member can be either an instance of 
        :class:`Member<groupy.objects.Member>` or a :class:`dict` containing 
        ``nickname`` and one of ``email``, ``phone_number``, or ``user_id``.

        :param members: members to add to the group
        :type members: :class:`list`
        :returns: the results ID of the add call
        :rtype: str
        """
        ids = (Member.identify(m) for m in members)
        r = api.Members.add(self.id, *ids)
        return r['results_id']

    def remove(self, member):
        """Remove a member from the group.

        :param member: the member to remove
        :type member: :class:`Member<groupy.objects.Member>`
        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: bool
        """
        try:
            api.Members.remove(self.id, member.user_id)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.OK
        return True


class Member(Recipient):
    """A GroupMe member.
    """
    def __init__(self, **kwargs):
        self.guid = kwargs.get('guid', None)    # set regardless of kwargs
        super().__init__(api.DirectMessages, 'direct_messages',
                         'user_id', **kwargs)

    def __repr__(self):
        return self.nickname

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

        A member is identified by their ``nickname`` and ``user_id`` properties.
        If the member does not yet have a GUID, a new one is created and
        assigned to them (and is returned alongside the ``nickname`` and
        ``user_id`` properties).

        :returns: the ``nickname``, ``user_id``, and ``guid`` of the member
        :rtype: :class:`dict`
        """
        return {
            'nickname': self.nickname,
            'user_id': self.user_id,
            'guid': self._guid         # new guid set if nonexistant
        }

    @classmethod
    def identify(cls, member):
        """Return or create an identification for a member.

        Member identification is required for adding them to groups. If member
        is a :class:`dict`, it must contain the following keys:

        - ``nickname``
        - ``user_id`` or ``email`` or ``phone_number``
        
        If an identification cannot be created then raise an
        :exc:`AttributeError<exceptions.AttributeError>`.

        :param member: either a :class:`Member<groupy.objects.Member>` or a
            :class:`dict` with the required keys
        :returns: the identification of member
        :rtype: :class:`dict`
        :raises AttributeError: if an identication cannot be made
        """
        try:
            return member.identification()
        except AttributeError:
            try:
                for id_type in ['user_id', 'email', 'phone_number']:
                    if id_type in member:
                        if 'guid' not in member:
                            member['guid'] = cls._next_guid()
                        return {
                            'nickname': member['nickname'],
                            'id_type': member[id_type],
                            'guid': member['guid']
                        }
            except AttributeError:
                raise AttributeError('no nickname')
            raise AttributeError('no user_id, email, or phone_number')


class Message(ApiResponse):
    """A GroupMe message.

    :param recipient: the reciever of the message
    :type recipient: :class:`Recipient<groupy.objects.Recipient>`
    """
    def __init__(self, recipient, **kwargs):
        self._recipient = recipient
        self.system = kwargs.pop('system', False)
        try:
            self._conversation_id = recipient.group_id
        except AttributeError:
            sender = User.get()
            participants = [sender.user_id, recipient.user_id]
            self._conversation_id = '+'.join(sorted(participants))
        super().__init__(**kwargs)

    def __repr__(self):
        msg = "{}: {}".format(self.name, self.text or "")
        if self.attachments:
            for a in self.attachments:
                msg += " +<{}>".format(str(a))
        return msg

    def __len__(self):
        """Return the length of the message text.
        """
        return len(self.text)

    def like(self):
        """Like the message.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: bool
        """
        try:
            api.Likes.create(self._conversation_id, self.id)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.OK
        return True

    def unlike(self):
        """Unlike the message.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: bool
        """
        try:
            api.Likes.destroy(self._conversation_id, self.id)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.OK
        return True

    def likes(self):
        """Return a :class:`FilterList<groupy.objects.FilterList>` of the
        members that like the message.
        
        :returns: a list of the members who "liked" this message
        :rtype: :class:`FilterList<groupy.objects.FilterList>`
        """
        liked = filter(
            lambda m: m.user_id in self.favorited_by,
            self._recipient.members())
        return FilterList(liked)


class Bot(ApiResponse):
    """A GroupMe bot.

    Each bot belongs to a single group. Messages posted by the bot are always
    posted to the group to which the bot belongs.
    """
    def __repr__(self):
        return self.name

    @classmethod
    def list(self):
        """Return a list of your bots.

        :returns: a list of your bots
        :rtype: :class:`FilterList<groupy.objects.FilterList>`
        """
        return FilterList(Bot(**b) for b in api.Bots.index())

    def post(self, text, picture_url=None):
        """Post a message to the group of the bot.

        :param str text: the message text
        :param str picture_url: the GroupMe image URL for an image
        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: bool
        """
        try:
            api.Bot.post(self.bot_id, text, picture_url)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.CREATED
        return True

    def destroy(self):
        """Destroy the bot.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: bool
        """
        try:
            api.Bot.destroy(self.bot_id)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.OK
        return True


class User(ApiResponse):
    """A GroupMe user.

    This is you, as determined by your API key.
    """
    def __repr__(self):
        return self.name

    @classmethod
    def get(cls):
        """Return your user information.

        :returns: your user information
        :rtype: :class:`dict`
        """
        return cls(**api.Users.me())

    def enable_sms(self, duration=4, registration_token=None):
        """Enable SMS mode.

        Enabling SMS mode causes GroupMe to send a text message for each
        message sent to the group.

        :param int duration: the number of hours for which to send text
            messages
        :param str registration_token: the push notification token for
            for which messages should be suppressed; if omitted, the user
            will recieve both push notifications as well as text messages
        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        try:
            api.Sms.create(duration, registration_token)
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.CREATED
        return True

    def disable_sms(self):
        """Disable SMS mode.

        Disabling SMS mode causes push notifications to resume and SMS text
        messages to be discontinued.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        try:
            api.Sms.delete()
        except errors.InvalidResponse as e:
            return e.args[0].status_code == status.OK
        return True


class Attachment:
    """A GroupMe attachment.

    Attachments are polymorphic objects representing either an image, location,
    split, or emoji. Use one of the factory methods to create an attachment.
    """
    def __init__(self, type_, **kwargs):
        self.type = type_
        for k, v in kwargs.items():
            setattr(self, k, v)

    def as_dict(self):
        return self.__dict__

    def __repr__(self):
        if self.type == 'image':
            return self.url
        elif self.type == 'location':
            return "{}: ({}, {})".format(self.name, self.lat, self.lng)
        elif self.type == 'split':
            return "split={}".format(self.token)
        elif self.type == 'emoji':
            return "{}: {}".format(self.placeholder, json.dumps(self.charmap))

    @classmethod
    def image(cls, url):
        """Create an image attachment.

        :param str url: the GroupMe image URL for an image
        :returns: image attachment
        :rtype: :class:`Attachment<groupy.objects.Attachment>`
        """
        return cls('image', url=url)

    @classmethod
    def new_image(cls, image):
        """Create an image attachment for a local image.

        Note that this posts the image to the image service API and uses the
        returned URL to create an image attachment.

        :param image: a file-like object containing an image
        :type image: :obj:`file`
        :returns: image attachment
        :rtype: :class:`Attachment<groupy.objects.Attachment>`
        """
        return cls.image(api.Images.create(image)['url'])

    @classmethod
    def location(cls, name, lat, lng):
        """Create a location attachment.

        :param str name: the name of the location
        :param float lat: the latitude component
        :param float lng: the longitude component
        :returns: a location attachment
        :rtype: :class:`Attachment<groupy.objects.Attachment>`
        """
        return cls('location', name=name, lat=lat, lng=lng)

    @classmethod
    def split(cls, token):
        """Create a split attachment.

        .. note::

            The split attachment is depreciated according to GroupMe.

        :param str token: the split token
        :returns: a split attachment
        :rtype: :class:`Attachment<groupy.objects.Attachment>`
        """
        return cls('split', token=token)

    @classmethod
    def emoji(cls, placeholder, charmap):
        """Create an emoji attachment.

        :param str placeholder: a high code-point character
        :param charmap: a two-dimensional charmap
        :type charmap: :class:`list`
        :returns: an emoji attachment
        :rtype: :class:`Attachment<groupy.objects.Attachment>`
        """
        return cls('emoji', placeholder=placeholder, charmap=charmap)
