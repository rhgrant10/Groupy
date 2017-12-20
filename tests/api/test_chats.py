import unittest
from unittest import mock

from groupy import pagers
from groupy.api import chats


class ChatsTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.chats = chats.Chats(self.m_session)


class ListChatsTests(ChatsTests):
    def setUp(self):
        super().setUp()
        m_chat = {
            'other_user': {'id': 42},
            'created_at': 123457890,
            'updated_at': 123457891,
        }
        self.m_session.get.return_value = mock.Mock(data=[m_chat])
        self.results = self.chats.list()

    def test_results_contains_chats(self):
        self.assertTrue(all(isinstance(c, chats.Chat) for c in self.results))

    def test_results_is_a_ChatList(self):
        self.assertTrue(isinstance(self.results, pagers.ChatList))


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        m_chat = {
            'other_user': {'id': 42, 'name': 'foo'},
            'created_at': 123457890,
            'updated_at': 123457891,
        }
        self.chat = chats.Chat(self.m_manager, **m_chat)

    def test_repr(self):
        representation = repr(self.chat)
        self.assertEqual(representation, "<Chat(other_user='foo')>")

    def test_post_uses_create(self):
        self.chat.messages = mock.Mock()
        self.chat.post()
        self.assertTrue(self.chat.messages.create.called)
