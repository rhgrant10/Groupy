import unittest
from unittest import mock


def get_fake_response(code=200, data=None):
    response = mock.Mock()
    response.status_code = code
    response.data = data
    return response


def get_fake_member_data(**kwargs):
    data = {
        'id': 'foo',
        'user_id': 'baz',
        'nickname': 'nick',
    }
    data.update(kwargs)
    return data


def get_fake_group_data(**kwargs):
    group_data = {
        'id': 'foo',
        'name': 'foobar',
        'group_id': 'bar',
        'created_at': 1302623328,
        'updated_at': 1302623329,
        'office_mode': False,
    }
    group_data.update(kwargs)
    return group_data


def get_fake_generic_message_data(**kwargs):
    data = {
        'id': 'foo',
        'created_at': 1302623328,
    }
    data.update(kwargs)
    return data


def get_fake_message_data(**kwargs):
    data = get_fake_generic_message_data()
    data['group_id'] = 'bar'
    data.update(kwargs)
    return data


def get_fake_direct_message_data(**kwargs):
    data = get_fake_generic_message_data()
    data['recipient_id'] = 'bar'
    data['sender_id'] = 'baz'
    data.update(kwargs)
    return data


class TestCase(unittest.TestCase):
    def assert_kwargs(self, mock, **kwargs):
        __, m_kwargs = mock.call_args
        for k, v in kwargs.items():
            with self.subTest(key=k, value=v):
                self.assertEqual(m_kwargs.get(k), v)
