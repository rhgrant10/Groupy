from datetime import datetime

from . import base
from . import messages
from . import memberships
from groupy import utils
from groupy import pagers


class Groups(base.Manager):
    def __init__(self, session):
        super().__init__(session, path='groups')

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        return [Group(self, **group) for group in response.data]

    def list(self, **params):
        return pagers.GroupList(self, **params)

    def list_former(self, **params):
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

    def change_owners(self, group_id, owner_id):
        url = utils.urljoin(self.url, 'change_owners')
        requests = [{'group_id': group_id, 'owner_id': owner_id}]
        payload = {'requests': requests}
        response = self.session.post(url, json=payload)
        result, = response.data['results']  # should be exactly one
        return ChangeOwnersResult(**result)


class ChangeOwnersResult:
    success_code = '200'
    status_texts = {
        '200': 'everything checked out',
        '400': 'the group is already owned by that user',
        '403': 'you must own a group to change its owner',
        '404': 'either the new owner is not a member of the group, or the '
               'new owner or the group were not found',
        '405': 'request object is missing required field or any of the '
               'required fields is not an ID',
    }

    def __init__(self, group_id, owner_id, status):
        self.group_id = group_id
        self.owner_id = owner_id
        self.status = status
        self.reason = self.status_texts.get(status, 'unknown')

    @property
    def is_success(self):
        return self.status == self.success_code

    def __bool__(self):
        return self.is_success


class Group(base.Resource):
    def __init__(self, manager, **data):
        super().__init__(manager, **data)
        self.messages = messages.Messages(self.manager.session, self.id)
        self.gallery = messages.Gallery(self.manager.session, self.group_id)
        self.leaderboard = messages.Leaderboard(self.manager.session, self.id)
        self.memberships = memberships.Memberships(self.manager.session, self.id)

        members = self.data.get('members') or []
        self.members = [memberships.Member(self.manager, self.id, **m) for m in members]
        self.created_at = datetime.fromtimestamp(self.created_at)
        self.updated_at = datetime.fromtimestamp(self.updated_at)

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    def post(self, text=None, attachments=None):
        return self.messages.create(text, attachments)

    def update(self, **details):
        return self.manager.update(id=self.id, **details)

    def destroy(self):
        return self.manager.destroy(id=self.id)

    def rejoin(self):
        return self.manager.rejoin(group_id=self.group_id)

    def refresh_from_server(self):
        group = self.manager.get(id=self.id)
        self.data = group.data

    def has_omission(self, field):
        try:
            value = getattr(self, field)
            return value != self.data[field]
        except AttributeError:
            return field in self.data
        except KeyError:
            return True
