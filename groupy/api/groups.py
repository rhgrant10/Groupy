from datetime import datetime

from . import base
from . import bots
from . import messages
from . import memberships
from groupy import utils
from groupy import pagers


class Groups(base.Manager):
    """A group manager."""

    def __init__(self, session):
        super().__init__(session, path='groups')

    def _raw_list(self, **params):
        response = self.session.get(self.url, params=params)
        if response.status_code == 304:
            return []
        return [Group(self, **group) for group in response.data]

    def list(self, page=1, per_page=10, omit=None):
        """List groups by page.

        The API allows certain fields to be excluded from the results so that
        very large groups can be fetched without exceeding the maximum
        response size. At the time of this writing, only 'memberships' is
        supported.

        :param int page: page number
        :param int per_page: number of groups per page
        :param int omit: a comma-separated list of fields to exclude
        :return: a list of groups
        :rtype: :class:`~groupy.pagers.GroupList`
        """
        return pagers.GroupList(self, self._raw_list, page=page,
                                per_page=per_page, omit=omit)

    def list_former(self):
        """List all former groups.

        :return: a list of groups
        :rtype: :class:`list`
        """
        url = utils.urljoin(self.url, 'former')
        response = self.session.get(url)
        return [Group(self, **group) for group in response.data]

    def get(self, id):
        """Get a single group by ID.

        :param str id: a group ID
        :return: a group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        url = utils.urljoin(self.url, id)
        response = self.session.get(url)
        return Group(self, **response.data)

    def create(self, name, **details):
        """Create a new group.response

        :param str name: the name of the group
        :param kwargs details: additional group fields
        :return: a new group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        payload = dict(details, name=name)
        response = self.session.post(self.url, json=payload)
        return Group(self, **response.data)

    def update(self, id, **details):
        """Update the details of a group.

        :param str id: a group ID
        :param kwargs details: values to update
        """
        url = utils.urljoin(self.url, id)
        response = self.session.post(url, json=details)
        return Group(self, **response.data)

    def destroy(self, id):
        """Destroy a group.

        :param str id: a group ID
        :return: ``True`` if successful
        :rtype: bool
        """
        path = '{}/destroy'.format(id)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return response.ok

    def join(self, group_id, share_token):
        """Join a group using a share token.

        :param str group_id: the group_id of a group
        :param str share_token: the share token
        :return: the group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        path = '{}/join/{}'.format(group_id, share_token)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        group = response.data['group']
        return Group(self, **group)

    def rejoin(self, group_id):
        """Rejoin a former group.

        :param str group_id: the group_id of a group
        :return: the group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        url = utils.urljoin(self.url, 'join')
        payload = {'group_id': group_id}
        response = self.session.post(url, json=payload)
        return Group(self, **response.data)

    def change_owners(self, group_id, owner_id):
        """Change the owner of a group.

        .. note:: you must be the owner to change owners

        :param str group_id: the group_id of a group
        :param str owner_id: the ID of the new owner
        :return: the result
        :rtype: :class:`~groupy.api.groups.ChangeOwnersResult`
        """
        url = utils.urljoin(self.url, 'change_owners')
        requests = [{'group_id': group_id, 'owner_id': owner_id}]
        payload = {'requests': requests}
        response = self.session.post(url, json=payload)
        result, = response.data['results']  # should be exactly one
        return ChangeOwnersResult(**result)


class ChangeOwnersResult:
    """The result of requesting a group owner change.

    :param str group_id: group_id of the group
    :param str owner_id: the ID of the new owner
    :param str status: the status of the request
    """

    #: the status that represents success
    success_code = '200'

    #: a map of statuses to meanings
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
        """Return ``True`` if the request was successful."""
        return self.status == self.success_code

    def __bool__(self):
        return self.is_success


class Group(base.ManagedResource):
    """A group."""

    def __init__(self, manager, **data):
        super().__init__(manager, **data)
        self.messages = messages.Messages(self.manager.session, self.id)
        self.gallery = messages.Gallery(self.manager.session, self.group_id)
        self.leaderboard = messages.Leaderboard(self.manager.session, self.id)
        self.memberships = memberships.Memberships(self.manager.session, self.id)
        self._bots = bots.Bots(self.manager.session)

        members = self.data.get('members') or []
        self.members = [memberships.Member(self.manager, self.id, **m) for m in members]
        self.created_at = datetime.fromtimestamp(self.data['created_at'])
        self.updated_at = datetime.fromtimestamp(self.data['updated_at'])

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    def post(self, text=None, attachments=None):
        """Post a new message to the group.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: the message
        :rtype: :class:`~groupy.api.messages.Message`
        """
        return self.messages.create(text=text, attachments=attachments)

    def update(self, **details):
        """Update the details of a group.

        :param kwargs details: updated values
        :return: an updated group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        return self.manager.update(id=self.id, **details)

    def destroy(self):
        """Destroy the group.

        Note that you must be the owner.

        :return: ``True`` if successful
        :rtype: bool
        """
        return self.manager.destroy(id=self.id)

    def rejoin(self):
        """Rejoin the group.

        Note that this must be a former group.

        :return: a current (not former) group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        return self.manager.rejoin(group_id=self.group_id)

    def refresh_from_server(self):
        """Refresh the group from the server in place."""
        group = self.manager.get(id=self.id)
        self.__init__(self.manager, **group.data)

    def create_bot(self, name, **details):
        """Create a bot in the group.

        :param str name: the name of the bot
        :param kwargs details: additional bot details
        :return: the created bot
        :rtype: :class:`~groupy.api.bots.Bot`
        """
        return self._bots.create(name, self.group_id, **details)

    def change_owners(self, user_id):
        """Change the owner of the group.

        Note that the user must be a member of the group.

        :param str user_id: the user_id of the new owner
        :return: the result
        :rtype: :class:`~groupy.api.groups.ChangeOwnersResult`
        """
        return self.manager.change_owners(self.group_id, user_id)
