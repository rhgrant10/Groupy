"""
.. module:: test_responses

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

Unit tests for the responses module.

"""
import unittest
from unittest import mock
from mock import call

import groupy
from groupy.object.responses import Recipient


class RecipientLengthTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        recipient = Recipient(mock_endpoint(), 'm', 'i', i='idkey', m='mkey')
        recipient.message_count = 10
        self.recipient = recipient

    def test_length_is_zero_if_no_messages(self):
        self.assertEqual(len(self.recipient), 10)


class RecipientPostEmptyMessageTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        recipient = Recipient(mock_endpoint(), 'm', 'i', i='idkey', m='mkey')
        self.recipient = recipient

    def test_message_must_contain_text_or_attachments(self):
        with self.assertRaises(ValueError):
            self.recipient.post(text=None)


class RecipientPostShortMessageTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        self.recipient = Recipient(mock_endpoint(), 'm', 'i',
                                                    i='idkey', m='mkey')
        self.recipient.post('test message')
        self.mock_create = self.recipient._endpoint.create

    def test_post_short_message_calls_endpoint_once(self):
        self.assertEqual(self.mock_create.call_count, 1)

    def test_post_short_message_calls_endpoint_with_id_key(self):
        self.mock_create.assert_called_with('idkey', 'test message')


class RecipientPostLongMessageTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        # TODO: Fix this literal dependency!
        self.chunks = ('x' * 1000, 'x' * 100)
        self.recipient = Recipient(mock_endpoint(), 'm', 'i',
                                                    i='idkey', m='mkey')
        self.recipient.post(''.join(self.chunks))
        self.mock_create = self.recipient._endpoint.create

    def test_post_long_message_calls_endpoint_twice(self):
        self.assertEqual(self.mock_create.call_count, 2)

    def test_post_long_message_calls_endpoint_with_each_chunk(self):
        calls = [call('idkey', self.chunks[0]), call('idkey', self.chunks[1])]
        self.mock_create.assert_has_calls(calls)


class RecipientChunkifyTests(unittest.TestCase):
    def test_text_shorter_than_chunk_size_remain_one_chunk(self):
        chunks = Recipient._chunkify('x', 2)
        self.assertEqual(len(chunks), 1)

    def test_text_equal_to_chunk_size_remains_one_chunk(self):
        chunks = Recipient._chunkify('xx', 2)
        self.assertEqual(len(chunks), 1)

    def test_text_longer_than_chunk_size_gets_split(self):
        chunks = Recipient._chunkify('xxx', 2)
        self.assertEqual(len(chunks), 2)

    def test_text_as_None_returns_one_None_chunk(self):
        chunks = Recipient._chunkify(None)
        self.assertEqual(chunks, [None])

    def test_empty_text_returns_one_None_chunk(self):
        chunks = Recipient._chunkify('')
        self.assertEqual(chunks, [None])

    def test_chunkify_breaks_across_whitespace_if_possible(self):
        chunks = Recipient._chunkify('abc 123', 5)
        self.assertEqual(chunks, ['abc', '123'])

    def test_chunkify_breaks_words_if_no_whitespace(self):
        chunks = Recipient._chunkify('abc123', 5)
        self.assertEqual(chunks, ['abc12', '3'])


@mock.patch('groupy.object.responses.Message')
@mock.patch('groupy.object.responses.MessagePager', autospec=True)
class RecipientMessagesTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        self.recipient = Recipient(mock_endpoint(), 'm', 'i',
                                                    i='idkey', m='mkey')
        self.mock_index = self.recipient._endpoint.index

    def test_messages_calls_MessagePager_once(self, MockMP, MockM):
        messages = self.recipient.messages()
        self.assertEqual(MockMP.call_count, 1)

    def test_messages_calls_endpoint_index_once(self, MockMP, MockM):
        messages = self.recipient.messages()
        self.mock_index.assert_called_once_with(
            'idkey', after_id=None, since_id=None, before_id=None
        )

    def test_messages_returns_MessagePager(self, MockMP, MockM):
        messages = self.recipient.messages()
        self.assertEqual(messages.__class__, groupy.object.listers.MessagePager)

    def test_messages_after_index_arguments_use_after_id(self, MockMP, MockM):
        messages = self.recipient.messages(after=123)
        self.mock_index.assert_called_once_with('idkey', after_id=123,
                                                since_id=None, before_id=None)

    def test_messages_before_index_arguments_use_before_id(self, MockMP, MockM):
        messages = self.recipient.messages(before=123)
        self.mock_index.assert_called_once_with('idkey', after_id=None,
                                                since_id=None, before_id=123)

    def test_messages_since_index_arguments_use_since_id(self, MockMP, MockM):
        messages = self.recipient.messages(since=123)
        self.mock_index.assert_called_once_with('idkey', after_id=None,
                                                since_id=123, before_id=None)

    def test_messages_before_and_after_raises_ValueError(self, MockMP, MockM):
        with self.assertRaises(ValueError):
            messages = self.recipient.messages(before=12, after=34)

    def test_messages_before_and_since_raises_ValueError(self, MockMP, MockM):
        with self.assertRaises(ValueError):
            messages = self.recipient.messages(before=12, since=34)

    def test_messages_since_and_after_raises_ValueError(self, MockMP, MockM):
        with self.assertRaises(ValueError):
            messages = self.recipient.messages(since=12, after=34)

