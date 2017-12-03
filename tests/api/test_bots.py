import unittest
from unittest import mock

from groupy.api import bots


class BotsTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.bots = bots.Bots(self.m_session)


class ListBotsTests(BotsTests):
    def setUp(self):
        super().setUp()
        self.m_session.get.return_value = mock.Mock(data=[{'x': 'X'}])
        self.results = self.bots.list()

    def test_results_are_bots(self):
        self.assertTrue(all(isinstance(b, bots.Bot) for b in self.results))


class CreateBotsTests(BotsTests):
    def setUp(self):
        super().setUp()
        self.m_session.post.return_value = mock.Mock(data={'bot': {'x': 'X'}})
        self.result = self.bots.create(name='foo', group_id='bar', baz='qux')

    def test_result_is_bot(self):
        self.assertTrue(isinstance(self.result, bots.Bot))

    def test_name_is_in_payload(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['bot'].get('name'), 'foo')

    def test_group_id_is_in_payload(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['bot'].get('group_id'), 'bar')

    def test_details_in_payload(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['bot'].get('baz'), 'qux')


class PostAsBotTests(BotsTests):
    def setUp(self):
        super().setUp()
        self.m_session.post.return_value = mock.Mock(ok=True)


class TextOnlyPostTests(PostAsBotTests):
    def setUp(self):
        super().setUp()
        self.result = self.bots.post(bot_id='qux', text='foo')

    def test_payload_contains_bot_id(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        self.assertEqual(payload.get('bot_id'), 'qux')

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        self.assertEqual(payload.get('text'), 'foo')

    def test_payload_omits_attachments(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        self.assertNotIn('attachments', payload)

    def test_result_is_True(self):
        self.assertTrue(self.result)


class PostWithAttachmentsTests(PostAsBotTests):
    def setUp(self):
        super().setUp()
        attachment = mock.Mock()
        attachment.to_json.return_value = {'bar': 'baz'}
        self.result = self.bots.post(bot_id='qux', text='foo',
                                     attachments=[attachment])

    def test_payload_contains_bot_id(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        self.assertEqual(payload.get('bot_id'), 'qux')

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        self.assertEqual(payload.get('text'), 'foo')

    def test_payload_contains_attachments(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs.get('json') or {}
        attachments = payload.get('attachments')
        self.assertEqual(attachments, [{'bar': 'baz'}])

    def test_result_is_True(self):
        self.assertTrue(self.result)


class DestroyBotTests(BotsTests):
    def setUp(self):
        super().setUp()
        self.result = self.bots.destroy(bot_id='foo')

    def test_result_is_True(self):
        self.assertTrue(self.result)


class BotTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        self.bot_id = 'foo'
        self.bot = bots.Bot(self.m_manager, name='bob', bot_id=self.bot_id)
        self.attachment = mock.Mock()
        self.result = self.bot.post(text='hi', attachments=[self.attachment])

    def test_post_uses_bot_id(self):
        args, __ = self.m_manager.post.call_args
        self.assertEqual(args[0], self.bot_id)

    def test_repr_contains_pertinent_info(self):
        representation = repr(self.bot)
        self.assertEqual(representation, "<Bot(name='bob')>")
