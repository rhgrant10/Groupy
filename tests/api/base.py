import unittest
from unittest import mock


def get_fake_response(code=200, data=None):
    response = mock.Mock()
    response.status_code = code
    response.data = data
    return response


class TestCase(unittest.TestCase):
    def assert_kwargs(self, mock, **kwargs):
        __, m_kwargs = mock.call_args
        for k, v in kwargs.items():
            with self.subTest(key=k, value=v):
                self.assertEqual(m_kwargs.get(k), v)
