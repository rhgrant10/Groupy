from . import base


class Blocks(base.Manager):
    """Blocks manager.

    :param session: the request session
    :type session: :class:`~groupy.session.Session`
    :param str user_id: your user ID
    """

    def __init__(self, session, user_id):
        super().__init__(session, 'blocks')
        self.user_id = user_id

    def list(self):
        """List the users you have blocked.

        :return: a list of :class:`~groupy.api.blocks.Block`'s
        :rtype: :class:`list`
        """
        params = {'user': self.user_id}
        response = self.session.get(self.url, params=params)
        blocks = response.data['blocks']
        return [Block(self, **block) for block in blocks]

    def between(self, other_user_id):
        """Check if there is a block between you and the given user.

        :return: ``True`` if the given user has been blocked
        :rtype: bool
        """
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.get(self.url, params=params)
        return response.data['between']

    def block(self, other_user_id):
        """Block the given user.

        :param str other_user_id: the ID of the user to block
        :return: the block created
        :rtype: :class:`~groupy.api.blocks.Block`
        """
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.post(self.url, params=params)
        block = response.data['block']
        return Block(self, **block)

    def unblock(self, other_user_id):
        """Unblock the given user.

        :param str other_user_id: the ID of the user to unblock
        :return: ``True`` if successful
        :rtype: bool
        """
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.delete(self.url, params=params)
        return response.ok


class Block(base.ManagedResource):
    """A block between you and another user."""

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(blocked_user_id={!r})>'.format(klass, self.blocked_user_id)

    def __eq__(self, other):
        return self.user_id == other.user_id and self.blocked_user_id == other.blocked_user_id

    def exists(self):
        """Return ``True`` if the block still exists.

        :return: ``True`` if the block exists
        :rtype: bool
        """
        return self.manager.between(other_user_id=self.blocked_user_id)

    def unblock(self):
        """Remove the block.

        :return: ``True`` if successful
        :rtype: bool
        """
        return self.manager.unblock(other_user_id=self.blocked_user_id)
