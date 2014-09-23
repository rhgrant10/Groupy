from .. import endpoint
from .. import errors
from ... import config

import unittest
import requests
import responses
import json
import re
from unittest import mock


def fake_response(response=None, code=200, errors=None):
    r = requests.Response()
    r.status_code = code
    if response is None:
        content_ = ' '
    else:
        content_ = json.dumps(envelope(response, code, errors))
    r._content = content_.encode('utf-8')
    return r
    

def envelope(response=None, code=200, errors=None):
    env = {
        'response': response,
        'meta': {
            'code': code
        }
    }
    if errors is not None:
        env['meta']['errors'] = errors
    return env


class UrlBuildingTests(unittest.TestCase):
    def setUp(self):
        self.known_urls = [
            ((None, []), config.API_URL),
            ((23, []), "/".join([config.API_URL, '23'])),
            (('somepath', []), "/".join([config.API_URL, 'somepath'])),
            (('somepath/', []), "/".join([config.API_URL, 'somepath/'])),
            (('/somepath', []), "/".join([config.API_URL, '/somepath'])),
            (('/somepath/', []), "/".join([config.API_URL, '/somepath/'])),
            (('somepath/{}', [23]), "/".join([config.API_URL, 'somepath/23'])),
            (('{}/somepath', [23]), "/".join([config.API_URL, '23/somepath'])),
            (('/{}/somepath', [23]), "/".join([config.API_URL, '/23/somepath'])),
            (('/{}/{}/', [23, 45]), "/".join([config.API_URL, '/23/45/'])),
            (('/{}/{}/{}', [23, 45, 67]), "/".join([config.API_URL, '/23/45/67']))
        ]
        
        self.known_errors = [
            (('{}', []), errors.UrlBuildError),
            (('{}{}', [23]), errors.UrlBuildError),
            (('{}{}{}', [23, 45]), errors.UrlBuildError),
        ]
        
    def test_correct_url_from_valid_input(self):
        for (path, args), correct_url in self.known_urls:
            with self.subTest(path=path, args=args):
                url = endpoint.Endpoint.build_url(path, *args)
                url_no_qs = url.split('?', 1)[0]
                self.assertEqual(url_no_qs, correct_url)
                
    def test_throws_correct_error_for_invalid_input(self):
        for (path, args), e_cls in self.known_errors:
            with self.subTest(path=path, args=args):
                with self.assertRaises(e_cls):
                    url = endpoint.Endpoint.build_url(path, *args)

    
class EndPointTests(unittest.TestCase):
    def setUp(self):
        self.token = 'token={}'.format(config.API_KEY)
        
    def test_response_extraction_no_errors(self):
        correct = {'key': 'value'}
        for code in [200, 300, 400, 500]:
            with self.subTest(code=code):
                response = endpoint.Endpoint.response(
                    fake_response(correct, code)
                    )
                self.assertEqual(response, correct)

    def test_response_extraction_with_errors(self):
        for code in [200, 300, 400, 500]:
            with self.subTest(code=code):
                with self.assertRaises(errors.ApiError):
                    extracted = endpoint.Endpoint.response(
                        fake_response(
                            {'key': 'value'},
                            code,
                            ['error']))

    def test_response_extraction_with_empty_response(self):
        self.assertIsNone(endpoint.Endpoint.response(fake_response()))
        for code in [300, 400, 500]:
            with self.subTest(code=code):
                with self.assertRaises(errors.ApiError):
                    endpoint.Endpoint.response(fake_response(code=code))
            
    def test_clamp(self):
        cases = [
            ( 0,  1,  3,  1),
            ( 1,  1,  3,  1),
            ( 2,  1,  3,  2),
            ( 3,  1,  3,  3),
            ( 4,  1,  3,  3),
            ( 0, -3, -1, -1),
            (-1, -3, -1, -1),
            (-2, -3, -1, -2),
            (-3, -3, -1, -3),
            (-4, -3, -1, -3),
            ( 0,  0,  0,  0)
        ]
        for value, lower, upper, answer in cases:
            with self.subTest(value=value):
                cvalue = endpoint.Endpoint.clamp(value, lower, upper)
                self.assertEqual(cvalue, answer)
                cvalue = endpoint.Endpoint.clamp(value, upper, lower)
                self.assertEqual(cvalue, answer)


class CorrectUrlMixin:
    def assert_url_correct(self, method, url_re, request, args, kwargs):
        responses.add(method, url_re)
        # Make the request
        request(*args, **kwargs)
        requested_url, param_str = \
            responses.calls[0].request.url.split('?', 1)
        self.assertRegex(requested_url, url_re)
        params = list(kwargs.keys()) + ['token']
        for i, p in enumerate(self.pregexes(*params)):
            self.assertRegex(
                param_str, p, 'missing param {!r}'.format(params[i]))

    @staticmethod
    def pregexes(*param_names):
        return list(map(
            lambda p: re.compile(r'\b{}=[-a-zA-Z0-9.+%_]+'.format(p)),
            param_names
        ))


class GroupsTests(unittest.TestCase, CorrectUrlMixin):
    def setUp(self):
        self.token = 'token={}'.format(config.API_KEY)
        
    def test_show_throws_TypeError_if_no_args(self):
        with self.assertRaises(TypeError):
            endpoint.Groups.show()

    @responses.activate
    def test_show_calls_correct_url(self):
        url_re = re.compile(
            r'{}/groups/\d+\?{}'.format(config.API_URL, self.token)
        )
        responses.add(responses.GET, url_re, match_querystring=True)
        for i, group_id in enumerate([1, 10, 100, 1000, 10000]):
            with self.subTest(group_id=group_id):
                url = '{}/groups/{}?{}'.format(
                    config.API_URL, group_id, self.token
                )
                # Perform and test.
                endpoint.Groups.show(group_id)
                self.assertEqual(responses.calls[i].request.url, url)
    


    @responses.activate
    def test_index_calls_correct_url(self):
        url_re = re.compile(
            r'^{}/groups'.format(config.API_URL)
        )
        i = 0
        for page in range(1, 10):
            for per_page in range(1, 500, 50):
                params = {
                    'page': page,
                    'per_page': per_page
                }
                with self.subTest(**params):
                    self.assert_url_correct(responses.GET, url_re,
                        endpoint.Groups.index, [], params)
                i += 1

    @responses.activate
    def test_create_calls_correct_url(self):
        url_re = re.compile(
            r'{}/groups'.format(config.API_URL)
        )
        self.assert_url_correct(responses.POST, url_re,
            endpoint.Groups.create,
            [], {
                'name': 'name',
                'description': 'description one',
                'image_url': 'http://i.groupme.com/someimage.png',
                'share': True
            }
        )
    
    @responses.activate
    def test_update_calls_correct_url(self):
        url_re = re.compile(
            r'{}/groups/\d+/update'.format(config.API_URL)
        )
        self.assert_url_correct(responses.POST, url_re,
            endpoint.Groups.update,
            ['123456789'], {
                'name': 'name',
                'description': 'description one',
                'image_url': 'http://i.groupme.com/someimage.png',
                'share': True
            }
        )
        
    @responses.activate
    def test_destroy_calls_correct_url(self):
        url_re = re.compile(
            r'{}/groups/\d+/destroy'.format(config.API_URL)
        )
        self.assert_url_correct(responses.POST, url_re,
            endpoint.Groups.destroy,
            ['123456789'], {}
        )


class MembersTests(unittest.TestCase, CorrectUrlMixin):
    def test_add_calls_correct_url(self):
        url = '{}/groups/123456789/members/add'.format(config.API_URL)
        responses.add(responses.POST, url,
            
            )
        
    
if __name__ == '__main__':
    unittest.main()