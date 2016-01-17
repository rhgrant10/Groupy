import json
import urllib
import unittest
from urllib.parse import urlsplit
from unittest.mock import patch
from unittest.mock import mock_open

import requests
import responses

from groupy import config
from groupy.api import errors
from groupy.api import endpoint


def fake_response(code=200, errors=None, **kwargs):
    r = requests.Response()
    r.status_code = code
    parcel = envelope(code=code, errors=errors, **kwargs)
    if parcel:
        data = json.dumps(parcel)
    else:
        data = ' '
    r._content = data.encode('utf-8')
    return r


def envelope(code=200, errors=None, **kwargs):
    """Return a response envelope."""
    if not kwargs:
        return None
    env = {'meta': {'code': code}}
    if errors is not None:
        env['meta']['errors'] = errors
    return dict(env, **kwargs)


def setUpModule():
    endpoint.Endpoint.url = 'http://example.com'
    config.API_KEY = 'TOKEN'


class UrlBuildingTests(unittest.TestCase):
    def test_token_included_as_param(self):
        url = endpoint.Endpoint.build_url()
        params = urlsplit(url).query
        self.assertIn('token=TOKEN', params)

    def test_no_path_and_no_args(self):
        url = endpoint.Endpoint.build_url()
        path = urlsplit(url).path
        self.assertEqual(path, '')

    def test_literal_path(self):
        url = endpoint.Endpoint.build_url('path')
        path = urlsplit(url).path
        self.assertEqual(path, '/path')

    def test_extra_args_arg_ignored(self):
        url = endpoint.Endpoint.build_url('path', 1)
        path = urlsplit(url).path
        self.assertEqual(path, '/path')

    def test_one_numeric_arg(self):
        url = endpoint.Endpoint.build_url('{}', 1)
        path = urlsplit(url).path
        self.assertEqual(path, '/1')

    def test_multiple_numeric_args(self):
        url = endpoint.Endpoint.build_url('{}/{}', 1, 2)
        path = urlsplit(url).path
        self.assertEqual(path, '/1/2')

    def test_one_string_arg(self):
        url = endpoint.Endpoint.build_url('{}', 'arg1')
        path = urlsplit(url).path
        self.assertEqual(path, '/arg1')

    def test_multiple_string_args(self):
        url = endpoint.Endpoint.build_url('{}/{}', 'arg1', 'arg2')
        path = urlsplit(url).path
        self.assertEqual(path, '/arg1/arg2')

    def test_multiple_string_args_used_in_order_given(self):
        url = endpoint.Endpoint.build_url('{}/{}', 'arg2', 'arg1')
        path = urlsplit(url).path
        self.assertEqual(path, '/arg2/arg1')

    def test_nonstring_path_converted_to_string(self):
        url = endpoint.Endpoint.build_url(list())
        path = urlsplit(url).path
        self.assertEqual(path, '/[]')

    def test_not_enough_args_raises_IndexError(self):
        with self.assertRaises(IndexError):
            endpoint.Endpoint.build_url('{}')

    def test_nonstring_endpoint_url_raises_TypeError_with_no_args(self):
        old = endpoint.Endpoint.url
        endpoint.Endpoint.url = object()
        with self.assertRaises(TypeError):
            endpoint.Endpoint.build_url()
        endpoint.Endpoint.url = old

    def test_nonstring_endpoint_url_raises_TypeError_with_path(self):
        old = endpoint.Endpoint.url
        endpoint.Endpoint.url = object()
        with self.assertRaises(TypeError):
            endpoint.Endpoint.build_url('path')
        endpoint.Endpoint.url = old

    def test_nonstring_endpoint_url_raises_TypeError_with_path_and_args(self):
        old = endpoint.Endpoint.url
        endpoint.Endpoint.url = object()
        with self.assertRaises(TypeError):
            endpoint.Endpoint.build_url('path', 'arg')
        endpoint.Endpoint.url = old


class ResponseExtractionTests(unittest.TestCase):
    def test_response_extracted_when_no_errors(self):
        without_errors = fake_response(response='content')
        response = endpoint.Endpoint.response(without_errors)
        self.assertEqual(response, 'content')

    def test_response_with_errors_raises_ApiError(self):
        with_errors = fake_response(response='content', errors=['error1'])
        with self.assertRaises(errors.ApiError):
            endpoint.Endpoint.response(with_errors)


class EqualClampTests(unittest.TestCase):
    def test_value_lower_and_upper_are_zero(self):
        result = endpoint.Endpoint.clamp(0, lower=0, upper=0)
        self.assertEqual(result, 0)

    def test_value_lower_and_upper_are_positive(self):
        result = endpoint.Endpoint.clamp(1, lower=1, upper=1)
        self.assertEqual(result, 1)

    def test_value_lower_and_upper_are_negative(self):
        result = endpoint.Endpoint.clamp(-1, lower=-1, upper=-1)
        self.assertEqual(result, -1)


class ClampTests(unittest.TestCase):
    def test_value_between_lower_and_upper_produces_value(self):
        lower, value, upper = 1, 2, 3
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, value)

    def test_value_is_less_than_lower_produces_lower(self):
        lower, value, upper = 2, 1, 3
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, lower)

    def test_value_is_more_than_upper_produces_upper(self):
        lower, value, upper = 1, 3, 2
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, upper)


class InvertedClampTests(unittest.TestCase):
    def test_value_between_lower_and_upper_produces_given_lower(self):
        lower, value, upper = 3, 2, 1
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, lower)

    def test_value_is_greatest_produces_given_lower(self):
        value, lower, upper = 3, 2, 1
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, lower)

    def test_value_is_least_produces_given_lower(self):
        lower, upper, value = 3, 2, 1
        result = endpoint.Endpoint.clamp(value, lower=lower, upper=upper)
        self.assertEqual(result, lower)


class CorrectUrlTests(unittest.TestCase):
    def assert_url_correct(self, method, url_, request, *args, **kwargs):
        # Mock the request.
        responses.add(method, url_)

        # Make the request. ApiErrors are ok.
        try:
            request(*args, **kwargs)
        except errors.ApiError:
            pass

        # Split the params from the URL.
        parts = responses.calls[0].request.url.split('?', 1)
        if len(parts) == 1:
            requested_url, param_str = parts[0], None
        else:
            requested_url, param_str = parts

        # Check the URL.
        self.assertEqual(requested_url, url_)

        # Check the params. Allow for the API token to be found.
        if param_str is None:
            return
        kvparams = map(lambda s: s.split('='), param_str.split('&'))
        for k, v in filter(lambda i: i[0] != 'token', kvparams):
            self.assertIn(k, kwargs)
            self.assertEqual(str(kwargs[k]), urllib.parse.unquote(v))

    @responses.activate
    def test_group_index(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/groups',
            endpoint.Groups.index, page=12, per_page=34)

    @responses.activate
    def test_groups_show(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/groups/1',
            endpoint.Groups.show, '1'
        )

    @responses.activate
    def test_groups_create(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups',
            endpoint.Groups.create,
            name='name', description='one',
            image_url='http://i.groupme.com/someimage.png',
            share=True
        )

    @responses.activate
    def test_groups_update(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups/1/update',
            endpoint.Groups.update, '1',
            name='name',
            description='one',
            image_url='http://i.groupme.com/someimage.png',
            share=True
        )

    @responses.activate
    def test_groups_destroy(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups/1/destroy',
            endpoint.Groups.destroy, '1'
        )

    @responses.activate
    def test_members_add(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups/1/members/add',
            endpoint.Members.add, '1'
        )

    @responses.activate
    def test_members_results(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/groups/1/members/results/2',
            endpoint.Members.results, '1', '2'
        )

    @responses.activate
    def test_members_remove(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups/1/members/2/remove',
            endpoint.Members.remove, '1', '2'
        )

    @responses.activate
    def test_messages_index(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/groups/1/messages',
            endpoint.Messages.index, '1',
            limit=100
        )

    @responses.activate
    def test_messages_create(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/groups/1/messages',
            endpoint.Messages.create, '1', 'Hello test'
        )

    @responses.activate
    def test_direct_messages_index(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/direct_messages',
            endpoint.DirectMessages.index,
            other_user_id='1',
            before_id='2',
            since_id='3',
            after_id='4'
        )

    @responses.activate
    def test_direct_messages_create(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/direct_messages',
            endpoint.DirectMessages.create, '1', 'Hello test'
        )

    @responses.activate
    def test_likes_create(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/messages/1/2/like',
            endpoint.Likes.create, '1', '2'
        )

    @responses.activate
    def test_likes_destroy(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/messages/1/2/unlike',
            endpoint.Likes.destroy, '1', '2'
        )

    @responses.activate
    def test_bots_index(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/bots',
            endpoint.Bots.index
        )

    @responses.activate
    def test_bots_create(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/bots',
            endpoint.Bots.create,
            name='name',
            group_id='group_id',
            avatar_url='avatar_url',
            callback_url='callback_url'
        )

    @responses.activate
    def test_bots_post(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/bots/post',
            endpoint.Bots.post,
            bot_id='bot_id',
            text='Hello',
            picture_url='picture_url'
        )

    @responses.activate
    def test_bots_destroy(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/bots/destroy',
            endpoint.Bots.destroy,
            bot_id='bot_id'
        )

    @responses.activate
    def test_users_me(self):
        self.assert_url_correct(
            responses.GET,
            'https://api.groupme.com/v3/users/me',
            endpoint.Users.me
        )

    @responses.activate
    def test_sms_enable(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/users/sms_mode',
            endpoint.Sms.create,
            duration=1,
            registration_id='2'
        )

    @responses.activate
    def test_sms_disable(self):
        self.assert_url_correct(
            responses.POST,
            'https://api.groupme.com/v3/users/sms_mode/delete',
            endpoint.Sms.delete
        )

    @responses.activate
    def test_images_create(self):
        with patch('builtins.open', mock_open()):
            self.assert_url_correct(
                responses.POST,
                'https://image.groupme.com/pictures',
                endpoint.Images.create,
                image=open('nosuchfile')
            )

    @responses.activate
    def test_images_download(self):
        self.assert_url_correct(
            responses.GET,
            'https://i.groupme.com/123456789.jpg',
            endpoint.Images.download,
            url='https://i.groupme.com/123456789.jpg'
        )


class MessageListingArgTests(unittest.TestCase):
    def test_multiple_message_ids_raises_ValueError(self):
        with self.assertRaises(ValueError):
            endpoint.Messages.index(1, before_id='10', after_id='5')


class ImageResponseTests(unittest.TestCase):
    def test_payload_returned_from_json(self):
        payload = endpoint.Images.response(fake_response(payload='content'))
        self.assertEqual(payload, 'content')


if __name__ == '__main__':
    unittest.main()
