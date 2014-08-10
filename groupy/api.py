import requests
import time
import json
from . import config
from . import errors

class Api:
	url = config.API_URL
	
	@classmethod
	def build_url(cls, path=None, *args):
		try:
			url = '/'.join([cls.url, path.format(*args)])
		except AttributeError:
			if path is None:
				url = cls.url
			else:
				url = '/'.join([cls.url, str(path)])
		except TypeError:
			url = cls.url
		return '?'.join([url, 'token={}'.format(config.API_KEY)])

	@classmethod
	def response(cls, r):
		try:
			data = r.json()
		except ValueError:
			raise errors.InvalidResponseError(r)
		if data['meta'].get("errors"):
			raise errors.GroupMeError(data['meta'])
		return data["response"]
	
	@staticmethod
	def clamp(value, lower, upper):
		return max(lower, min(value, upper))


class Groups(Api):
	url = '/'.join([Api.url, 'groups'])

	@classmethod
	def show(cls, group_id):
		r = requests.get(
			cls.build_url(group_id)
		)
		return cls.response(r)

	@classmethod
	def index(cls, page=1, per_page=500, former=False):
		per_page = cls.clamp(per_page, 1, 500)
		r = requests.get(
			cls.build_url('former') if former else cls.build_url(),
			params={
				'page': page,
				'per_page': per_page
			}
		)
		return cls.response(r)

	@classmethod
	def create(cls, name, description=None, image_url=None, share=True):
		r = requests.post(
			cls.build_url(), 
			params={
				'name': name,
				'description': description,
				'image_url': image_url,
				'share': share
			}
		)
		return cls.response(r)

	@classmethod
	def update(cls, group_id, name=None, description=None, share=None, image_url=None):
		r = requests.post(
			cls.build_url('{}/update', group_id), 
			params={
				'name': name,
				'description': description,
				'image_url': image_url,
				'share': share
			}
		)
		return objects.Group(**cls.response(r))

	@classmethod
	def destroy(cls, group_id):
		r = requests.post(
			cls.build_url('{}/destroy', group_id)
		)
		return cls.response(r)


class Members(Api):
	url = '/'.join([Api.url, 'groups'])

	@classmethod
	def add(cls, group_id, *members):
		r = requests.post(
			cls.build_url('{}/members/add', group_id),
			data=json.dumps({'members': members}),
			headers={'content-type': 'application/json'})
		return cls.response(r)

	@classmethod
	def results(cls, group_id, result_id):
		r = requests.get(
			cls.build_url('{}/members/results/{}', group_id, result_id)
		)
		return cls.response(r)

	@classmethod
	def remove(cls, group_id, member_id):
		r = requests.post(
			cls.build_url('{}/members/{}/remove', group_id, member_id)
		)
		return cls.response(r)


class Messages(Api):
	url = '/'.join([Api.url, 'groups'])

	@classmethod
	def index(cls, group_id, before_id=None, since_id=None, after_id=None, limit=100):
		limit = cls.clamp(limit, 1, 100)
		r = requests.get(
			cls.build_url('{}/messages', group_id),
			params={
				'after_id': after_id,
				'limit': limit,
				'before_id': before_id,
				'since_id': since_id
			}
		)
		return cls.response(r)

	@classmethod
	def create(cls, group_id, text, *attachments):
		r = requests.post(
			cls.build_url('{}/messages', group_id),
			data=json.dumps({
				'message': {
					'source_guid': str(time.time()),
					'text': text,
					'attachments': attachments
				}
			}),
			headers={'content-type': 'application/json'}
		)
		return cls.response(r)


class DirectMessages(Api):
	url = '/'.join([Api.url, 'direct_messages'])
	
	@classmethod
	def index(cls, other_user_id, before_id=None, since_id=None):
		r = requests.get(
			cls.build_url(),
			params={
				'other_user_id': other_user_id,
				'before_id': before_id,
				'since_id': since_id
			}
		)
		return cls.response(r)

	@classmethod
	def create(cls, recipient_id, text, *attachments):
		r = requests.post(
			cls.build_url(),
			data=json.dumps({
				'direct_message': {
					'source_guid': str(time.time()),
					'recipient_id': recipient_id,
					'text': text,
					'attachments': attachments
				}
			}),
			headers={'content-type': 'application/json'}
		)
		return cls.response(r)


class Likes(Api):
	url = '/'.join([Api.url, 'messages'])

	@classmethod
	def create(cls, conversation_id, message_id):
		r = requests.post(
			cls.build_url('{}/{}/like', conversation_id, message_id)
		)
		return cls.response(r)

	@classmethod
	def destroy(cls, conversation_id, message_id):
		r = requests.post(
			cls.build_url('{}/{}/unlike', conversation_id, message_id)
		)
		return cls.response(r)


class Bots(Api):
	url = '/'.join([Api.url, 'bots'])

	@classmethod
	def index(cls):
		r = requests.get(
			cls.build_url()
		)
		return cls.response(r)

	@classmethod
	def create(cls, name, group_id, avatar_url=None, callback_url=None):
		r = requests.post(
			cls.build_url(),
			params={
				'name': name,
				'group_id': group_id,
				'avatar_url': avatar_url,
				'callback_url': callback_url
			}
		)
		return cls.response(r)

	@classmethod
	def post(cls, bot_id, text, picture_url=None):
		r = requests.post(
			cls.build_url('post'),
			params={
				'bot_id': bot_id,
				'text': text,
				'picture_url': picture_url
			}
		)
		return cls.response(r)

	@classmethod
	def destroy(cls, bot_id):
		r = requests.post(
			cls.build_url('destroy'),
			params={'bot_id': bot_id}
		)
		return cls.response(r)

class Users(Api):
	url = '/'.join([Api.url, 'users'])

	@classmethod
	def me(cls):
		r = requests.get(
			cls.build_url('me')
		)
		return cls.response(r)


class Sms(Api):
	url = '/'.join([Api.url, 'users/sms_mode'])

	@classmethod
	def create(cls, duration=4, registration_id=None):
		r = requests.post(
			cls.build_url(),
			params={
				'duration': duration,
				'registration_id': registration_id
			}
		)
		return cls.response(r)

	@classmethod
	def delete(cls):
		r = requests.post(
			cls.build_url('delete')
		)
		return cls.response(r)


class Images(Api):
	url = '/'.join([config.IMAGE_API_URL, 'pictures'])

	@classmethod
	def response(cls, r):
		try:
			data = r.json()
		except ValueError:
			raise InvalidResponseError(r)
		return data['payload']

	@classmethod
	def create(cls, image):
		r = requests.post(
			cls.build_url(),
			files={'file': image}
		)
		return cls.response(r)
