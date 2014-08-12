from . import api
from . import status
from . import errors
import operator

class FilterList(list):
	"""A filterable list.

	Acts just like a regular list, except it can be filtered using a special
	keyword syntax. Also, the first and last items are special properties.

	"""
	def filter(self, **kwargs):
		"""Filter the list and return a new instance.

		Arguments are keyword arguments only, and can be appended with 
		operator method names to indicate relationships other than equals.
		For example, to filter the list down to only items with a name
		containing 'ie':

		.. code-block:: python

			new_list = filter_list.filter(name__contains='ie')

		As another example, this filters the list down to only those
		with a created property that is less than 1234567890:

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
		:class:`errors.InvalidOperatorError`.

		:return: a new list with potentially less items than the original
		:rtype: :class:`FilterList`
		"""
		kvops = []
		for k, v in kwargs.items():
			if '__' in k[1:-1]:
				k, o = k.rsplit('__', 1)
				try:
					op = getattr(operator, o)
				except AttributeError:
					raise errors.InvalidOperatorError("__{}".format(o))
			else:
				op = operator.eq
			kvops.append((k, v, op))
		return FilterList(filter(
			lambda i: all(hasattr(i, k) and op(getattr(i, k), v) for k, v, op in kvops),
			self
		))

	def sort(self, key, reverse=False):
		"""Return the same items in a new list but sorted.

		:param str key: the name of the property on which to sort
		:param bool reverse: ``True`` if the order should be reversed, 
			``False`` otherwise.
		:return: a new sorted list of the items in the original list
		:rtype: :class:`FilterList`
		"""
		return FilterList(sorted(self, key=lambda x: getattr(x, key, 0), reverse=reverse))

	@property
	def first(self):
	    return self[0]

	@property
	def last(self):
		return self[-1]


class MessagePager(FilterList):
	"""A filterable, extendable page of messages.

	:param Group group: the group from which to page through messages
	:param list messages: the initial page of messages
	:param bool backward: ``True`` if the oldest message is at index 0, 
		``False`` otherwise
	"""
	def __init__(self, group, messages, backward=False):
		super().__init__(messages)
		self.backward = backward
		self.group = group

	@property
	def oldest(self):
	    return self.first if self.backward else self.last
	
	@property
	def newest(self):
	    return self.last if self.backward else self.first

	def prepend(self, messages):
		"""Prepend a list of messages.

		:param list messages: the messages to prepend
		"""
		for each in messages:
			self.insert(0, each)

	def newer(self):
		"""Return the next (newer) page of messages.
		"""
		return self.group.messages(after=self.newest.id)
		
	def older(self):
		"""Return the previous (older) page of messages.
		"""
		return self.group.messages(before=self.oldest.id)
		
	def inewer(self):
		"""Add in-place the next (newer) page of messages.
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
		"""
		old = self.older()
		if not old:
			return False
		if self.backward:
			self.prepend(self.older())
		else:
			self.extend(self.older())
		return True


class Group:
	"""A GroupMe group.
	"""
	def __init__(self, **kwargs):
		messages = kwargs.pop('messages', {})
		self.message_count = messages.get('count')
		self.last_message_id = messages.get('last_message_id')
		self.last_message_created_at = messages.get('last_message_created_at')
		self._members = [Member(**m) for m in kwargs.pop('members')]
		if 'max_memberships' in kwargs:
			self.max_members = kwargs.pop('max_memberships')
		else:
			self.max_members = kwargs.pop('max_members')
		self.__dict__.update(**kwargs)

	def __str__(self):
		return "{}, {}/{} members, {} messages".format(
				self.name, len(self.members()),
				self.max_members, self.message_count)

	def __len__(self):
		"""Return the number of messages in the group.
		"""
		return self.message_count

	@classmethod
	def list(cls, former=False):
		"""List all of your current or former groups.
		"""
		# Former groups come as a single page.
		if former:
			return FilterList(Group(**g) for g in api.Groups.index(former=True))
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

	def refresh(self):
		"""Update the group with new information from the API.
		"""
		self.__init__(**api.Groups.show(self.id))

	def messages(self, before=None, since=None, after=None, limit=None):
		"""Return a page of messages from the group.

		:param str before: a reference message ID
		:param str since: a reference message ID
		:param str after: a reference message ID
		:param int limit: maximum number of messages to include in the page
		"""
		try:
			r = api.Messages.index(self.id, before_id=before, since_id=since, after_id=after)
		except errors.InvalidResponseError as e:
			if e.args[0].status_code != 304:
				raise e
			return None 	# No more messages.
		self.message_count = r['count']		# Update the message count.
		return MessagePager(self, (Message(**m) for m in r['messages']), backward=after is not None)

	def post(self, text, *attachments):
		"""Post a message to the group.

		.. note::

			Messages with no text must have at least one attachment.

		.. note::

			Messages with a text longer than the maximum allowed length will be
			split into multiple messages. If attachments exist then are posted 
			in the last message.

		:param str text: the message text
		:param list attachments: a list of attachments to include
		"""
		if not text and not attachments:
			raise ArgumentError('must be one attachment or text')
		*chunks, last = self._chunkify(text)
		sent = []
		for chunk in chunks:
			sent.append(api.Messages.create(self.id, chunk))
		sent.append(api.Messages.create(self.id, last, *attachments))
		return sent

	def members(self):
		"""Return a list of the members in the group.
		"""
		return FilterList(self._members)

	def add(self, *members):
		"""Add a member to a group.

		Each member can be either an instance of :class:`Member` or a
		``dict`` containing ``'nickname'`` and one of ``'email'``, 
		``'phone_number'``, or ``'user_id'``.

		:param list members: members to add to the group
		:return: the results ID of the add call
		:rtype: str
		"""
		ids = (Member.idenify(m) for m in members)
		r = api.Members.add(self.id, *ids)
		return r['results_id']

	def remove(self, member):
		"""Remove a member from the group.

		:param :class:`Member` member: the member to remove
		"""
		try:
			r = api.Members.remove(self.id, member.user_id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True


class Member:
	"""A GroupMe member.
	"""
	def __init__(self, **kwargs):
		self.guid = kwargs.get('guid', None)
		self.__dict__.update(kwargs)

	def __str__(self):
		return self.nickname

	@property
	def guid(self):
		if not self._guid:
			self._guid = self._next_guid()
		return self._guid
	@guid.setter
	def guid(self, value):
		self._guid = value

	def identification(self):
		"""Return the identification of the member.

		A member is identified by their nickname and user_id properties. If the
		member does not yet have a GUID, a new one is created and assigned to
		them (and is returned alongside the nickname and user_id properties).
		"""
		return {
			'nickname': self.nickname,
			'user_id': self.user_id,
			'guid': self._guid 		# new guid set if nonexistant
		}

	# Create and return a new guid based on the current time.
	@staticmethod
	def _next_guid():
		return str(time.time())

	@classmethod
	def identify(cls, member):
		"""Return or create an identification for a member.

		:param member: either a :class:`Member` or a ``dict``; if the latter,
			it must contain at least a ``nickname`` property as well as one of 
			``user_id``, ``email``, or ``phone_number``
		:return: the identification of member
		:rtype: dict
		"""
		try:
			return member.identification()
		except AttributeError:
			try:
				for id_type in ['user_id', 'email', 'phone_number']:
					if id_type in member:
						if 'guid' not in member:
							member['guid'] = self._next_guid()
						return {
							'nickname': member['nickname'],
							'id_type': member[id_type],
							'guid': member['guid']
						}
			except AttributeError:
				raise AttributeError('no nickname')
			raise AttributeError('no user_id, email, or phone_number')

	def post(self, text, *attachments):
		pass

	def messages(self):
		pass


class Message:
	"""A GroupMe message.
	"""
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		msg = "{}: {}".format(self.name, self.text or "")
		if self.attachments:
			for a in self.attachments:
				msg += " +[{}]".format(a['type'])
		return msg

	def __len__(self):
		"""Return the length of the message text.
		"""
		return len(self.text)

	def like(self):
		"""Like the message.
		"""
		try:
			r = api.Likes.create(self.group_id, self.id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True

	def unlike(self):
		"""Unlike the message.
		"""
		try:
			r = api.Likes.destroy(self.group_id, self.id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True

	def likes(self):
		"""Return a :class:`FilterList` of the members that like the message.
		"""
		return FilterList(m for m in self.group.members() if m.user_id in self.favorited_by)


class Bot:
	"""A GroupMe bot.

	Each bot belongs to a single group. Messages posted by the bot are always
	posted to the group to which the bot belongs.
	"""
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		return self.name

	@classmethod
	def list(self):
		"""Return a :class:`FilterList` of the bots.
		"""
		return FilterList(Bot(**b) for b in api.Bots.index())

	def post(self, text, picture_url=None):
		"""Post a message to the group.

		:param str text: the message text
		:param str picture_url: the GroupMe image URL for an image
		:returns: ``True`` if successful, ``False`` otherwise
		:rtype: bool
		"""
		try:
			r = api.Bot.post(self.bot_id, text, picture_url)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.CREATED
		return True

	def destroy(self):
		"""Destroy the bot.

		:returns: ``True`` if successful, ``False`` otherwise
		:rtype: bool
		"""
		try:
			r = api.Bot.destroy(self.bot_id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True


class User:
	"""A GroupMe user.

	This is you, as determined by your API key.
	"""
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		return self.name

	@classmethod
	def get(cls):
		"""Return the user's information.
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
		:rtype: bool
		"""
		try:
			r = api.Sms.create(duration, registration_token)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.CREATED
		return True

	def disable_sms(self):
		"""Disable SMS mode.

		Disabling SMS mode causes push notifications to cease being suppressed,
		as well as discontinuation of SMS text messages.

		:returns: ``True`` if successful, ``False`` otherwise
		:rtype: bool
		"""
		try:
			r = api.Sms.delete()
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
		self.__dict__.update(kwargs)

	def as_dict(self):
		return self.__dict__

	@classmethod
	def image(cls, url):
		"""Create an image attachment.
		
		:param str url: the GroupMe image URL for an image
		:returns: image attachment
		:rtype: :class:`Attachment`
		"""
		return cls('image', url=url)

	@classmethod
	def new_image(cls, image):
		"""Create an image attachment for a local image.

		Note that this posts the image to the image service API and uses the
		returned URL to create an image attachment.

		:param file image: a file-like object containing an image
		:returns: image attachment
		:rtype: :class:`Attachment`
		"""
		return cls.image(api.Images.create(image)['url'])

	@classmethod
	def location(cls, name, lat, lng):
		"""Create a location attachment.

		:param str name: the name of the location
		:param float lat: the latitude component
		:param float lng: the longitude component
		:returns: a location attachment
		:rtype: :class:`Attachment`
		"""
		return cls('location', name=name, lat=lat, lng=lng)

	@classmethod
	def split(cls, token):
		"""Create a split attachment.

		:param str token: the split token
		:returns: a split attachment
		:rtype: :class:`Attachment`
		"""
		return cls('split', token=token)

	@classmethod
	def emoji(cls, placeholder, charmap):
		"""Create an emoji attachment.

		:param str placeholder: a high code-point character
		:param list charmap: a two-dimensional charmap
		:returns: an emoji attachment
		:rtype: :class:`Attachment`
		"""
		return cls('emoji', placeholder=placeholder, charmap=charmap)
