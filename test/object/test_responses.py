"""
.. module:: test_responses

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

Unit tests for the responses module.

Recipient(mock_endpoint, 'mkey', 'idkey'):
 - post()
 - post(None)
 - post('')
    * assert raises ValueError
 - post('some text')
    * calls it's endpoint.create method
        - once with arguments ('idkey', 'some text')
 - post('some text that ... is 500 chars in length')
    * calls it's endpoint.create method twice
        - once with arguments ('idkey', 'some text that ... ')
        - once with arguments ('idkey', 'is 500 chars in length')

"""
import unittest
from unittest import mock
from mock import call

import groupy
from groupy.object.responses import Recipient


class RecipientPostShortMessageTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        self.recipient = Recipient(mock_endpoint(), 'm', 'i', i='idkey', m='mkey')
        self.recipient.post('test message')
        self.mock_create = self.recipient._endpoint.create

    def test_post_short_message_calls_endpoint_once(self):
        self.assertEqual(self.mock_create.call_count, 1)

    def test_post_short_message_calls_endpoint_with_id_key(self):
        self.mock_create.assert_called_with('idkey', 'test message')


class RecipientPostLongMessageTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        self.recipient = Recipient(mock_endpoint(), 'm', 'i', i='idkey', m='mkey')
        self.chunks = ('x' * 450, 'x' * 100)
        self.recipient.post(''.join(self.chunks))
        self.mock_create = self.recipient._endpoint.create

    def test_post_long_message_calls_endpoint_twice(self):
        self.assertEqual(self.mock_create.call_count, 2)

    def test_post_long_message_calls_endpoint_with_each_chunk(self):
        calls = [call('idkey', self.chunks[0]), call('idkey', self.chunks[1])]
        self.mock_create.assert_has_calls(calls)


@mock.patch('groupy.object.responses.Message')
@mock.patch('groupy.object.responses.MessagePager')
class RecipientMessagesTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Endpoint')
    def setUp(self, mock_endpoint):
        self.recipient = Recipient(mock_endpoint(), 'm', 'i', i='idkey', m='mkey')

    def test_messages_calls_MessagePager_once(self, MockMessagePager, M):
        messages = self.recipient.messages()
        self.assertEqual(MockMessagePager.call_count, 1)

    def test_messages_calls_endpoint_index_once(self, MockMessagePager, M):
        messages = self.recipient.messages()
        self.recipient._endpoint.index.assert_called_once_with(
            'idkey', after_id=None, since_id=None, before_id=None
        )
