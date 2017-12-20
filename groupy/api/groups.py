from datetime import datetime

from . import base
from . import bots
from . import messages
from . import memberships
from . import user
from groupy import utils
from groupy import pagers
from groupy import exceptions


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

    def list_all(self, per_page=10, omit=None):
        """List all groups.

        Since the order of groups is determined by recent activity, this is the
        recommended way to obtain a list of all groups. See
        :func:`~groupy.api.groups.Groups.list` for details about ``omit``.

        :param int per_page: number of groups per page
        :param int omit: a comma-separated list of fields to exclude
        :return: a list of groups
        :rtype: :class:`~groupy.pagers.GroupList`
        """
        return self.list(per_page=per_page, omit=omit).autopage()

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

    def create(self, name, description=None, image_url=None, share=None, **kwargs):
        """Create a new group.

        Note that, although possible, there may be issues when not using an
        image URL from GroupMe's image service.

        :param str name: group name (140 characters maximum)
        :param str description: short description (255 characters maximum)
        :param str image_url: GroupMe image service URL
        :param bool share: whether to generate a share URL
        :return: a new group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        payload = {
            'name': name,
            'description': description,
            'image_url': image_url,
            'share': share,
        }
        payload.update(kwargs)
        response = self.session.post(self.url, json=payload)
        return Group(self, **response.data)

    def update(self, id, name=None, description=None, image_url=None,
               office_mode=None, share=None, **kwargs):
        """Update the details of a group.

        .. note::

            There are significant bugs in this endpoint!
            1. not providing ``name`` produces 400: "Topic can't be blank"
            2. not providing ``office_mode`` produces 500: "sql: Scan error on
            column index 14: sql/driver: couldn't convert <nil> (<nil>) into
            type bool"

            Note that these issues are "handled" automatically when calling
            update on a :class:`~groupy.api.groups.Group` object.

        :param str id: group ID
        :param str name: group name (140 characters maximum)
        :param str description: short description (255 characters maximum)
        :param str image_url: GroupMe image service URL
        :param bool office_mode: (undocumented)
        :param bool share: whether to generate a share URL
        :return: an updated group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        path = '{}/update'.format(id)
        url = utils.urljoin(self.url, path)
        payload = {
            'name': name,
            'description': description,
            'image_url': image_url,
            'office_mode': office_mode,
            'share': share,
        }
        payload.update(kwargs)
        response = self.session.post(url, json=payload)
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
        payload = {
            'requests': [{
                'group_id': group_id,
                'owner_id': owner_id,
            }],
        }
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
        self._user = user.User(self.manager.session)

        members = self.data.get('members') or []
        self.members = [memberships.Member(self.manager, self.id, **m) for m in members]
        self.created_at = utils.get_datetime(self.data['created_at'])
        self.updated_at = utils.get_datetime(self.data['updated_at'])

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    @property
    def is_mine(self):
        membership = self.get_membership()
        return 'owner' in membership.roles

    def post(self, text=None, attachments=None):
        """Post a new message to the group.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: the message
        :rtype: :class:`~groupy.api.messages.Message`
        """
        return self.messages.create(text=text, attachments=attachments)

    def update(self, name=None, description=None, image_url=None,
               office_mode=None, share=None, **kwargs):
        """Update the details of the group.

        :param str name: group name (140 characters maximum)
        :param str description: short description (255 characters maximum)
        :param str image_url: GroupMe image service URL
        :param bool office_mode: (undocumented)
        :param bool share: whether to generate a share URL
        :return: an updated group
        :rtype: :class:`~groupy.api.groups.Group`
        """
        # note we default to the current values for name and office_mode as a
        # work-around for issues with the group update endpoint
        if name is None:
            name = self.name
        if office_mode is None:
            office_mode = self.office_mode
        return self.manager.update(id=self.id, name=name, description=description,
                                   image_url=image_url, office_mode=office_mode,
                                   share=share, **kwargs)

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

    def create_bot(self, name, avatar_url=None, callback_url=None, dm_notification=None,
                   **kwargs):
        """Create a new bot in a particular group.

        :param str name: bot name
        :param str avatar_url: the URL of an image to use as an avatar
        :param str callback_url: a POST-back URL for each new message
        :param bool dm_notification: whether to POST-back for direct messages?
        :return: the new bot
        :rtype: :class:`~groupy.api.bots.Bot`
        """
        return self._bots.create(name=name, group_id=self.group_id,
                                 avatar_url=avatar_url, callback_url=callback_url,
                                 dm_notification=dm_notification)

    def change_owners(self, user_id):
        """Change the owner of the group.

        Note that the user must be a member of the group.

        :param str user_id: the user_id of the new owner
        :return: the result
        :rtype: :class:`~groupy.api.groups.ChangeOwnersResult`
        """
        return self.manager.change_owners(self.group_id, user_id)

    def get_membership(self):
        """Get your membership.

        Note that your membership may not exist. For example, you do not have
        a membership in a former group. Also, the group returned by the API
        when rejoining a former group does not contain your membership. You
        must call :func:`refresh_from_server` to update the list of members.

        :return: your membership in the group
        :rtype: :class:`~groupy.api.memberships.Member`
        :raises groupy.exceptions.MissingMembershipError: if your membership is
                not in the group data
        """
        user_id = self._user.me['user_id']
        for member in self.members:
            if member.user_id == user_id:
                return member
        raise exceptions.MissingMembershipError(self.group_id, user_id)

    def update_membership(self, nickname=None, **kwargs):
        """Update your own membership.

        Note that this fails on former groups.

        :param str nickname: new nickname
        :return: updated membership
        :rtype: :class:`~groupy.api.members.Member`
        """
        return self.memberships.update(nickname=nickname, **kwargs)

    def leave(self):
        """Leave the group.

        :return: ``True`` if successful
        :rtype: bool
        """
        membership = self.get_membership()
        return membership.remove()
