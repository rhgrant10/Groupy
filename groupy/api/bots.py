from . import base
from groupy import utils


class Bots(base.Manager):
    def __init__(self, session):
        super().__init__(session, path='bots')

    def list(self, **params):
        response = self.session.get(self.url, params=params)
        return [Bot(self, **bot) for bot in response.data]

    def create(self, name, group_id, **details):
        payload = dict(details, name=name, group_id=group_id)
        response = self.session.post(self.url, json=payload)
        return Bot(self, **response.data)

    def post(self, bot_id, text, attachments=None):
        url = utils.urljoin(self.url, 'post')
        payload = {
            'bot_id': bot_id,
            'text': text,
        }
        if attachments:
            payload['attachments'] = [a.to_json() for a in attachments]

        response = self.session.post(url, json=payload)
        return response.ok

    def destroy(self, id):
        path = '{}/destroy'.format(id)
        url = utils.urljoin(self.url, path)
        response = self.session.post(url)
        return response.ok


class Bot(base.Resource):
    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(name={!r})>'.format(klass, self.name)

    def post(self, text, attachments=None):
        return self.manager.post(self.bot_id, text, attachments)
