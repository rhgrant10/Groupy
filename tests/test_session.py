import unittest
from unittest import mock

import requests
import responses

from groupy import session
from groupy.exceptions import BadResponse
from groupy.exceptions import InvalidJsonError
from groupy.exceptions import MissingMetaError
from groupy.exceptions import MissingResponseError
from groupy.exceptions import NoResponse


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.token = 'abc123'
        self.session = session.Session(self.token)
        self.url = 'https://example.com/foo'

    @responses.activate
    def test_token_is_present_in_headers(self):
        responses.add(responses.GET, self.url)
        self.session.get(self.url)
        self.assertEqual(responses.calls[0].request.headers['x-access-token'],
                         self.token)

    def test_content_type_is_json(self):
        headers = self.session.headers or {}
        self.assertIn('content-type', headers)
        content_type = headers['content-type']
        self.assertEqual(content_type.lower(), 'application/json')

    @responses.activate
    def test_bad_response(self):
        responses.add(responses.GET, self.url, status=503)
        with self.assertRaises(BadResponse):
            self.session.get(self.url)

    @responses.activate
    def test_no_response(self):
        responses.add(responses.GET, self.url,
                      body=requests.exceptions.ConnectionError())
        with self.assertRaises(NoResponse):
            self.session.get(self.url)


class RequestTests(unittest.TestCase):
    @responses.activate
    def setUp(self):
        self.session = session.Session('abc123')
        self.url = 'https://example.com/foo'
        data = {'foo': 'bar'}
        errors = ['error1', 'error2']
        envelope = {
            'response': data,
            'meta': {
                'code': 200,
                'errors': errors,
            }
        }
        responses.add(responses.GET, self.url, json=envelope)
        self.response = self.session.get(self.url)

    def test_data_property(self):
        self.assertEqual(self.response.data, {'foo': 'bar'})

    def test_errors_property(self):
        self.assertEqual(self.response.errors, ['error1', 'error2'])


class ResponseTests(unittest.TestCase):
    def setUp(self):
        self.m_response = mock.MagicMock()
        self.json = self.get_json()
        setattr(self.m_response.json, *self.get_json())
        self.response = session.Response(self.m_response)

    def get_json(self):
        raise NotImplementedError


class MetaMissingTests(ResponseTests):
    def get_json(self):
        return 'return_value', {'response': 'foo'}

    def test_response_data_is_foo(self):
        self.assertEqual(self.response.data, 'foo')

    def test_response_errors_raises_missing_meta(self):
        with self.assertRaises(MissingMetaError):
            self.response.errors


class RespsonseMissingTests(ResponseTests):
    def get_json(self):
        return 'return_value', {'meta': {'errors': ['a', 'b']}}

    def test_response_data_raises_missing_response(self):
        with self.assertRaises(MissingResponseError):
            self.response.data

    def test_response_errors_is_a_b(self):
        self.assertEqual(self.response.errors, ['a', 'b'])


class InvalidJsonTests(ResponseTests):
    def get_json(self):
        return 'side_effect', ValueError('invalid json')

    def test_response_data_raises_invalid_json(self):
        with self.assertRaises(InvalidJsonError):
            self.response.data

    def test_response_errors_raises_invalid_json(self):
        with self.assertRaises(InvalidJsonError):
            self.response.errors
