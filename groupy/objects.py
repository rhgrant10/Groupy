from . import api
from . import status
from . import errors
import operator

class List(list):
	def filter(self, **kwargs):
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
		return List(filter(
			lambda i: all(hasattr(i, k) and op(getattr(i, k), v) for k, v, op in kvops),
			self
		))

	def sort(self, key, reverse=False):
		return List(sorted(self, key=lambda x: getattr(x, key, 0), reverse=reverse))

	@property
	def first(self):
	    return self[0]

	@property
	def last(self):
		return self[-1]


class MessageList(List):
	def __init__(self, group, iter, backward=False):
		super().__init__(iter)
		self.backward = backward
		self.group = group

	@property
	def oldest(self):
	    return self.first if self.backward else self.last
	
	@property
	def newest(self):
	    return self.last if self.backward else self.first

	def prepend(self, iter):
		for each in self.older():
			self.insert(0, each)

	def newer(self):
		return self.group.messages(after=self.newest.id)
		
	def older(self):
		return self.group.messages(before=self.oldest.id)
		
	def inewer(self):
		new = self.newer()
		if not new:
			return False
		if self.backward:
			self.extend(self.newer())
		else:
			self.prepend(self.newer())
		return True
		
	def iolder(self):
		old = self.older()
		if not old:
			return False
		if self.backward:
			self.prepend(self.older())
		else:
			self.extend(self.older())
		return True


class Group:
	def __init__(self, **kwargs):
		messages = kwargs.pop('messages', {})
		self.message_count = messages.get('count')
		self.last_message_id = messages.get('last_message_id')
		self.last_message_created_at = messages.get('last_message_created_at')
		self._members = [Member(**m) for m in kwargs.pop('members')]
		self.__dict__.update(**kwargs)

	def __str__(self):
		return "{}, {}/{} members, {} messages".format(
				self.name, len(self.members()),
				self.max_members, self.message_count)

	def __len__(self):
		return self.message_count

	@classmethod
	def list(cls):
		return List(Group(**g) for g in api.Groups.index())

	@classmethod
	def former_list(cls):
		return List(Group(**g) for g in api.Groups.index(former=True))

	@staticmethod
	def _chunkify(text, chunk_size=450):
		if text is None:
			return [None]
		chunks = []
		while len(text) > chunk_size:
			portion = text[:chunk_size]
			i = len(portion.rsplit(None, 1)[0])
			chunks.append(portion[:i].strip())
			text = text[i:].strip()
		chunks.append(text)
		return chunks

	def refresh(self):
		self.__init__(**api.Groups.show(self.id))

	def messages(self, before=None, since=None, after=None, limit=None):
		try:
			r = api.Messages.index(self.id, before_id=before, since_id=since, after_id=after)
		except errors.InvalidResponseError as e:
			if e.args[0].status_code != 304:
				raise e
			return None
		self.message_count = r['count']
		return MessageList(self, (Message(**m) for m in r['messages']), backward=after is not None)

	def post(self, text, *attachments):
		if not text and not attachments:
			raise ArgumentError('must be one attachment or text')
		*chunks, last = self._chunkify(text)
		sent = []
		for chunk in chunks:
			sent.append(api.Messages.create(self.id, chunk))
		sent.append(api.Messages.create(self.id, last, *attachments))
		return sent

	def members(self):
		return List(self._members)

	def add(self, *members):
		ids = (Member.idenify(m) for m in members)
		r = api.Members.add(self.id, *ids)
		return r['results_id']

	def remove(self, member):
		try:
			r = api.Members.remove(self.id, member.user_id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True


class Member:
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
		return {
			'nickname': self.nickname,
			'user_id': self.user_id,
			'guid': self.guid
		}

	@staticmethod
	def _next_guid():
		return str(time.time())

	@classmethod
	def identify(cls, member):
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


class Message:
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		msg = "{}: {}".format(self.name, self.text or "")
		if self.attachments:
			for a in self.attachments:
				msg += " +[{}]".format(a['type'])
		return msg

	def __len__(self):
		return len(self.text)

	def like(self):
		try:
			r = api.Likes.create(self.group_id, self.id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True

	def unlike(self):
		try:
			r = api.Likes.destroy(self.group_id, self.id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True

	def likes(self):
		return List(m for m in self.group.members() if m.user_id in self.favorited_by)


class Bot:
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		return self.name

	@classmethod
	def list(self):
		return List(Bot(**b) for b in api.Bots.index())

	def post(self, text, picture_url=None):
		try:
			r = api.Bot.post(self.bot_id, text, picture_url)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.CREATED
		return True

	def destroy(self):
		try:
			r = api.Bot.destroy(self.bot_id)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True


class User:
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def __str__(self):
		return self.name

	@classmethod
	def get(cls):
		return cls(**api.Users.me())

	def enable_sms(self, duration=4, registration_token=None):
		try:
			r = api.Sms.create(duration, registration_token)
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.CREATED
		return True

	def disable_sms(self):
		try:
			r = api.Sms.delete()
		except errors.InvalidResponse as e:
			return e.args[0].status_code == status.OK
		return True


class Attachment:
	def __init__(self, type_, **kwargs):
		self.type = type_
		self.__dict__.update(kwargs)

	def as_dict(self):
		return self.__dict__

	@classmethod
	def image(cls, url):
		return cls('image', url=url)

	@classmethod
	def new_image(cls, image):
		return cls.image(api.Images.create(image)['url'])

	@classmethod
	def location(cls, name, lat, lng):
		return cls('location', name=name, lat=lat, lng=lng)

	@classmethod
	def split(cls, token):
		return cls('split', token=token)

	@classmethod
	def emoji(cls, placeholder, charmap):
		return cls('emoji', placeholder=placeholder, charmap=charmap)
