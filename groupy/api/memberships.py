from collections import namedtuple
import time
import uuid

from . import base
from . import messages
from . import user
from groupy import utils
from groupy import exceptions


class Memberships(base.Manager):

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


class Member(base.Resource):
    def __init__(self, manager, group_id, **data):
        super().__init__(manager, **data)
        self.messages = messages.DirectMessages(self.manager.session,
                                                other_user_id=self.user_id)
        self._user = user.User(self.manager.session)
        self._memberships = Memberships(self.manager.session,
                                        group_id=group_id)

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(user_id={!r}, nickname={!r})>'.format(klass, self.user_id,
                                                          self.nickname)

    def is_blocked(self):
        return self._user.blocks.between(other_user_id=self.user_id)

    def block(self):
        return self._user.blocks.block(other_user_id=self.user_id)

    def unblock(self):
        return self._user.blocks.unblock(other_user_id=self.user_id)

    def remove(self):
        return self._memberships.remove(membership_id=self.id)


class MembershipRequest(base.Resource):

    Results = namedtuple('Results', 'members failures')

    def __init__(self, manager, *requests, **data):
        super().__init__(manager, **data)
        self._requests = requests
        self._expired_exception = None
        self._not_ready_exception = None
        self._is_ready = False
        self.results = None

    def _check_if_ready(self):
        try:
            results = self.manager.check(self.results_id)
            self._is_ready = True
            self._not_ready_exception = None
            self._process_new_members(results)
        except exceptions.ResultsNotReady as e:
            self._is_ready = False
            self._not_ready_exception = e
        except exceptions.ResultsExpired as e:
            self._is_ready = True
            self._expired_exception = e

    def _process_new_members(self, results):
        members = []
        failures = []
        data = {member['guid']: member for member in results}
        for request in self._requests:
            try:
                member_data = data[request['guid']]
            except KeyError:
                failures.append(request)
            else:
                member_data.pop('guid')
                member = Member(self.manager, **member_data)
                members.append(member)
        self.results = self.Results(members, failures)

    def is_ready(self):
        if not self._is_ready:
            self._check_if_ready()
        return self._is_ready

    def poll(self, timeout=30, interval=2):
        start = time.time()
        while time.time() - start < timeout and not self.is_ready():
            time.sleep(interval)
        return self.get()

    def get(self):
        if self._expired_exception:
            raise self._expired_exception
        if self._not_ready_exception:
            raise self._not_ready_exception
        return self.results
