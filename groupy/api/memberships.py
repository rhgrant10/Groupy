from collections import namedtuple
import time
import uuid

from . import base
from . import messages
from . import user
from groupy import utils
from groupy import exceptions


class Memberships(base.Manager):
    """A membership manager for a particular group.

    :param session: the request session
    :type session: :class:`~groupy.session.Session`
    :param str group_id: the group_id of a group
    """

    def __init__(self, session, group_id):
        path = 'groups/{}/members'.format(group_id)
        super().__init__(session, path=path)
        self.group_id = group_id

    def add(self, nickname, email=None, phone_number=None, user_id=None):
        """Add a user to the group.

        You must provide either the email, phone number, or user_id that
        uniquely identifies a user.

        :param str nickname: new name for the user in the group
        :param str email: email address of the user
        :param str phone_number: phone number of the user
        :param str user_id: user_id of the user
        :return: a membership request
        :rtype: :class:`MembershipRequest`
        """
        member = {
            'nickname': nickname,
            'email': email,
            'phone_number': phone_number,
            'user_id': user_id,
        }
        return self.add_multiple(member)

    def add_multiple(self, *users):
        """Add multiple users to the group at once.

        Each given user must be a dictionary containing a nickname and either
        an email, phone number, or user_id.

        :param args users: the users to add
        :return: a membership request
        :rtype: :class:`MembershipRequest`
        """
        guid = uuid.uuid4()
        for i, user_ in enumerate(users):
            user_['guid'] = '{}-{}'.format(guid, i)

        payload = {'members': users}
        url = utils.urljoin(self.url, 'add')
        response = self.session.post(url, json=payload)
        return MembershipRequest(self, *users, group_id=self.group_id,
                                 **response.data)

    def check(self, results_id):
        """Check for results of a membership request.

        :param str results_id: the ID of a membership request
        :return: successfully created memberships
        :rtype: :class:`list`
        :raises groupy.exceptions.ResultsNotReady: if the results are not ready
        :raises groupy.exceptions.ResultsExpired: if the results have expired
        """
        path = 'results/{}'.format(results_id)
        url = utils.urljoin(self.url, path)
        response = self.session.get(url)
        if response.status_code == 503:
            raise exceptions.ResultsNotReady(response)
        if response.status_code == 404:
            raise exceptions.ResultsExpired(response)
        return response.data['members']

    def update(self, nickname=None, **kwargs):
        """Update your own membership.

        Note that this fails on former groups.

        :param str nickname: new nickname
        :return: updated membership
        :rtype: :class:`~groupy.api.memberships.Member`
        """
        url = self.url + 'hips/update'
        payload = {
            'membership': {
                'nickname': nickname,
            },
        }
        payload['membership'].update(kwargs)
        response = self.session.post(url, json=payload)
        return Member(self, self.group_id, **response.data)

    def remove(self, membership_id):
        """Remove a member from the group.

        :param str membership_id: the ID of a member in this group
        :return: ``True`` if the member was successfully removed
        :rtype: bool
        """
        path = '{}/remove'.format(membership_id)
        url = utils.urljoin(self.url, path)
        payload = {'membership_id': membership_id}
        response = self.session.post(url, json=payload)
        return response.ok


class Member(base.ManagedResource):
    """A user's membership in a particular group.

    Members have both an ID and a membership ID. The membership ID is unique
    to the combination of user and group.

    It can be helpful to think of a "memmber" as a "membership." That is, a
    specific user in a specific group. Thus, two ``Member`` objects are
    equal only if their ``id`` fields are equal,. As a consequence, the two
    ``Member`` objects representing user A in two groups X and Y will _not_
    be equal.

    :param manager: a manager for the group of the membership
    :type manager: :class:`~groupy.api.base.Manager`
    :param str group_id: the group_id of the membership
    :param kwargs data: additional membership data
    """

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

    def __eq__(self, other):
        return self.id == other.id

    def post(self, text=None, attachments=None, source_guid=None):
        """Post a direct message to the user.

        :param str text: the message content
        :param attachments: message attachments
        :param str source_guid: a client-side unique ID for the message
        :return: the message sent
        :rtype: :class:`~groupy.api.messages.DirectMessage`
        """
        return self.messages.create(text=text, attachments=attachments,
                                    source_guid=source_guid)

    def is_blocked(self):
        """Check whether you have the user of the membership blocked.

        :return: ``True`` if the user is blocked
        :rtype: bool
        """
        return self._user.blocks.between(other_user_id=self.user_id)

    def block(self):
        """Block the user of the membership.

        :return: the block created
        :rtype: :class:`~groupy.api.blocks.Block`
        """
        return self._user.blocks.block(other_user_id=self.user_id)

    def unblock(self):
        """Unblock the user of the membership.

        :return: ``True`` if successfully unblocked
        :rtype: bool
        """
        return self._user.blocks.unblock(other_user_id=self.user_id)

    def remove(self):
        """Remove the member from the group (destroy the membership).

        :return: ``True`` if successfully removed
        :rtype: bool
        """
        return self._memberships.remove(membership_id=self.id)

    def add_to_group(self, group_id, nickname=None):
        """Add the member to another group.

        If a nickname is not provided the member's current nickname is used.

        :param str group_id: the group_id of a group
        :param str nickname: a new nickname
        :return: a membership request
        :rtype: :class:`MembershipRequest`
        """
        if nickname is None:
            nickname = self.nickname
        memberships = Memberships(self.manager.session, group_id=group_id)
        return memberships.add(nickname, user_id=self.user_id)


class MembershipRequest(base.ManagedResource):
    """A membership request.

    :param manager: a manager for the group of the membership
    :type manager: :class:`~groupy.api.base.Manager`
    :param args requests: the members requested to be added
    :param kwargs data: the membership request response data
    """

    Results = namedtuple('Results', 'members failures')

    def __init__(self, manager, *requests, **data):
        # data contains the results_id
        super().__init__(manager, **data)
        self.requests = requests
        self._expired_exception = None
        self._not_ready_exception = None
        self._is_ready = False
        self.results = None

    def check_if_ready(self):
        """Check for and fetch the results if ready."""
        try:
            results = self.manager.check(self.results_id)
        except exceptions.ResultsNotReady as e:
            self._is_ready = False
            self._not_ready_exception = e
        except exceptions.ResultsExpired as e:
            self._is_ready = True
            self._expired_exception = e
        else:
            failures = self.get_failed_requests(results)
            members = self.get_new_members(results)
            self.results = self.__class__.Results(list(members), list(failures))
            self._is_ready = True
            self._not_ready_exception = None

    def get_failed_requests(self, results):
        """Return the requests that failed.

        :param results: the results of a membership request check
        :type results: :class:`list`
        :return: the failed requests
        :rtype: generator
        """
        data = {member['guid']: member for member in results}
        for request in self.requests:
            if request['guid'] not in data:
                yield request

    def get_new_members(self, results):
        """Return the newly added members.

        :param results: the results of a membership request check
        :type results: :class:`list`
        :return: the successful requests, as :class:`~groupy.api.memberships.Members`
        :rtype: generator
        """
        for member in results:
            guid = member.pop('guid')
            yield Member(self.manager, self.group_id, **member)
            member['guid'] = guid

    def is_ready(self, check=True):
        """Return ``True`` if the results are ready.

        If you pass ``check=False``, no attempt is made to check again for
        results.

        :param bool check: whether to query for the results
        :return: ``True`` if the results are ready
        :rtype: bool
        """
        if not self._is_ready and check:
            self.check_if_ready()
        return self._is_ready

    def poll(self, timeout=30, interval=2):
        """Return the results when they become ready.

        :param int timeout: the maximum time to wait for the results
        :param float interval: the number of seconds between checks
        :return: the membership request result
        :rtype: :class:`~groupy.api.memberships.MembershipResult.Results`
        """
        time.sleep(interval)
        start = time.time()
        while time.time() - start < timeout and not self.is_ready():
            time.sleep(interval)
        return self.get()

    def get(self):
        """Return the results now.

        :return: the membership request results
        :rtype: :class:`~groupy.api.memberships.MembershipResult.Results`
        :raises groupy.exceptions.ResultsNotReady: if the results are not ready
        :raises groupy.exceptions.ResultsExpired: if the results have expired
        """
        if self._expired_exception:
            raise self._expired_exception
        if self._not_ready_exception:
            raise self._not_ready_exception
        return self.results
