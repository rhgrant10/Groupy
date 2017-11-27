from . import base
from . import blocks
from groupy import utils


class User(base.Manager):
    def __init__(self, session):
        super().__init__(session, 'users')
        self._me = None
        self._blocks = None
        self.sms_mode = SmsMode(self.session)

    @property
    def blocks(self):
        if self._blocks is None:
            self._blocks = blocks.Blocks(self.session, self.me['id'])
        return self._blocks

    @property
    def me(self):
        if self._me is None:
            self._me = self.get_me()
        return self._me

    def get_me(self):
        url = utils.urljoin(self.url, 'me')
        response = self.session.get(url)
        return response.data

    def update(self, **params):
        url = utils.urljoin(self.url, 'update')
        response = self.session.post(url, json=params)
        return response.data


class SmsMode(base.Manager):
    def __init__(self, session):
        super().__init__(session, 'users/sms_mode')

    def enable(self, duration, registration_id=None):
        payload = {'duration': duration}
        if registration_id is not None:
            payload['registration_id'] = registration_id
        response = self.session.post(self.url, json=payload)
        return response.ok

    def disable(self):
        url = utils.urljoin(self.url, 'delete')
        response = self.session.post(url)
        return response.ok
