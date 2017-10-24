from . import base


class Blocks(base.Manager):
    def __init__(self, session, user_id):
        super().__init__(session, 'blocks')
        self.user_id = user_id

    def list(self):
        params = {'user': self.user_id}
        response = self.session.get(self.url, params=params)
        blocks = response.data['blocks']
        return [Block(self, **block) for block in blocks]

    def between(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.get(self.url, params=params)
        return response.data['between']

    def block(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.post(self.url, params=params)
        block = response.data['block']
        return Block(self, **block)

    def unblock(self, other_user_id):
        params = {'user': self.user_id, 'otherUser': other_user_id}
        response = self.session.delete(self.url, params=params)
        return response.ok


class Block(base.Resource):
    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(blocked_user_id={!r})>'.format(klass, self.blocked_user_id)

    def exists(self):
        return self.manager.between(other_user_id=self.blocked_user_id)

    def unblock(self):
        return self.manager.unblock(other_user_id=self.blocked_user_id)
