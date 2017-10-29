from unittest import mock

from groupy.api import user
from .base import get_fake_response
from .base import TestCase


class UserTests(TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.m_session.get.return_value = get_fake_response(data={'id': 'foo'})
        self.user = user.User(self.m_session)

    def test_id_is_foo(self):
        self.assertEqual(self.user.me['id'], 'foo')

    @mock.patch('groupy.api.user.blocks')
    def test_blocks_uses_id(self, m_blocks):
        self.user.blocks
        (__, id_), __ = m_blocks.Blocks.call_args
        self.assertEqual(id_, 'foo')

    def test_update(self):
        data = {'bar': 'foo'}
        self.m_session.post.return_value = get_fake_response(data=data)
        result = self.user.update(foo='bar')
        self.assertEqual(result, data)


class SmsModeTests(TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.sms_mode = user.SmsMode(self.m_session)
        self.m_session.post.return_value = mock.Mock(ok=True)


class EnableSmsModeTests(SmsModeTests):
    def setUp(self):
        super().setUp()
        self.result = self.sms_mode.enable(duration=42)

    def test_result_is_True(self):
        self.assertTrue(self.result)

    def test_payload_is_correct(self):
        self.assert_kwargs(self.m_session.post, json={'duration': 42})


class EnableSmsModeWithRegistrationTests(SmsModeTests):
    def setUp(self):
        super().setUp()
        self.result = self.sms_mode.enable(duration=42, registration_id=420)

    def test_result_is_True(self):
        self.assertTrue(self.result)

    def test_payload_is_correct(self):
        payload = {'duration': 42, 'registration_id': 420}
        self.assert_kwargs(self.m_session.post, json=payload)


class DisableSmsModeTests(SmsModeTests):
    def setUp(self):
        super().setUp()
        self.result = self.sms_mode.disable()

    def test_result_is_True(self):
        self.assertTrue(self.result)
