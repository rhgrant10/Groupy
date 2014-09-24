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
    """Return a response envelope."""
    env = {
        'response': response,
        'meta': {'code': code}
    }
    if errors is not None:
        env['meta']['errors'] = errors
    return env


class UrlBuildingTests(unittest.TestCase):
    def test_valid_input(self):
        def url(*args):
            return '/'.join([config.API_URL] + list(args))
            
        cases = {
            (None, ()): url(),
            (1, ()): url('1'),
            ('somepath', ()): url('somepath'),
            ('somepath/', ()): url('somepath/'),
            ('/somepath', ()): url('/somepath'),
            ('/somepath/', ()): url('/somepath/'),
            ('somepath/{}', (1, )): url('somepath/1'),
            ('{}/somepath', (1, )): url('1/somepath'),
            ('/{}/somepath', (1, )): url('/1/somepath'),
            ('/{}/{}/', (1, 2)): url('/1/2/'),
            ('/{}/{}/{}', (1, 2, 3)): url('/1/2/3')
        }
        for (path, args), correct_url in cases.items():
            with self.subTest(path=path, args=args):
                url = endpoint.Endpoint.build_url(path, *args)
                url_no_qs = url.split('?', 1)[0]
                self.assertEqual(url_no_qs, correct_url)
                
    def test_invalid_input(self):
        cases = {
            ('{}', ()): IndexError,
            ('{}{}', (1,)): IndexError,
            ('{}{}{}', (1, 2)): IndexError,
        }
        for (path, args), err in cases.items():
            with self.subTest(path=path, args=args):
                with self.assertRaises(err):
                    url = endpoint.Endpoint.build_url(path, *args)

    
class ResponseExtractionTests(unittest.TestCase):
    def test_normal_response(self):
        correct = {'key': 'value'}
        for code in [200, 300, 400, 500]:
            with self.subTest(code=code):
                response = endpoint.Endpoint.response(
                    fake_response(correct, code)
                    )
                self.assertEqual(response, correct)

    def test_error_in_response(self):
        for code in [200, 300, 400, 500]:
            with self.subTest(code=code):
                with self.assertRaises(errors.ApiError):
                    extracted = endpoint.Endpoint.response(
                        fake_response(
                            {'key': 'value'},
                            code,
                            ['error']
                        )
                    )

    def test_empty_response(self):
        for code in [300, 400, 500]:
            with self.subTest(code=code):
                with self.assertRaises(errors.ApiError):
                    endpoint.Endpoint.response(fake_response(code=code))


class ClampTests(unittest.TestCase):
    def test_normal(self):
        cases = {
            ( 0, -1,  1):  0,
            (-1, -1,  1): -1,
            ( 1, -1,  1):  1,
            (-2, -1,  1): -1,
            ( 2, -1,  1):  1,
            ( 0,  0,  0):  0,
            ( 1,  1,  1):  1,
            (-1, -1, -1): -1
        }
        for (value, lower, upper), answer in cases.items():
            with self.subTest(value=value):
                cvalue = endpoint.Endpoint.clamp(value, lower, upper)
                self.assertEqual(cvalue, answer)
            
    def test_inverted_bounds(self):
        cases = {
            ( 0,  1, -1):  1,
            (-1,  1, -1):  1,
            ( 1,  1, -1):  1,
            (-2,  1, -1):  1,
            ( 2,  1, -1):  1,
        }
        for (value, lower, upper), answer in cases.items():
            with self.subTest(value=value):
                cvalue = endpoint.Endpoint.clamp(value, lower, upper)
                self.assertEqual(cvalue, answer)

        
class CorrectUrlTests(unittest.TestCase):
    def assert_url_correct(self, method, url_re, request, args, kwargs):
        responses.add(method, re.compile(url_re))
        # Make the request. ApiErrors are ok.
        try:
            request(*args, **kwargs)
        except errors.ApiError:
            pass
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

    @responses.activate
    def test_group_index(self):
        self.assert_url_correct(
            responses.GET,
            r'^{}/groups'.format(config.API_URL),
            endpoint.Groups.index,
            [], {'page': 12, 'per_page': 34}
        )
    
    @responses.activate
    def test_groups_show(self):
        self.assert_url_correct(
            responses.GET,
            r'{}/groups/\d+'.format(config.API_URL),
            endpoint.Groups.show,
            [23], {}
        )

    @responses.activate
    def test_groups_create(self):
        self.assert_url_correct(
            responses.POST,
            r'{}/groups'.format(config.API_URL),
            endpoint.Groups.create,
            [],
            {
                'name': 'name',
                'description': 'description one',
                'image_url': 'http://i.groupme.com/someimage.png',
                'share': True
            }
        )
    
    @responses.activate
    def test_groups_update(self):
        self.assert_url_correct(
            responses.POST,
            r'{}/groups/\d+/update'.format(config.API_URL),
            endpoint.Groups.update,
            ['123456789'],
            {
                'name': 'name',
                'description': 'description one',
                'image_url': 'http://i.groupme.com/someimage.png',
                'share': True
            }
        )
        
    @responses.activate
    def test_groups_destroy(self):
        self.assert_url_correct(
            responses.POST,
            r'{}/groups/\d+/destroy'.format(config.API_URL),
            endpoint.Groups.destroy,
            ['123456789'],
            {}
        )
        
    @responses.activate
    def test_messages_index(self):
        self.assert_url_correct(
            responses.GET, 
            r'{}/groups/\d+/messages'.format(config.API_URL),
            endpoint.Messages.index,
            [12], {}
        )
        
    @responses.activate
    def test_members_add(self):
        self.assert_url_correct(responses.POST,
            r'{}/groups/\d+/members/add'.format(config.API_URL),
            endpoint.Members.add,
            [12, {'members': [{
                'user_id': '1234567',
                'nickname': 'Fred',
                'guid': '1234567890'}]}],
            {}
        )

    @responses.activate
    def test_members_results(self):
        self.assert_url_correct(
            responses.GET,
            r'{}/groups/\d+/members/results/\d+'.format(config.API_URL),
            endpoint.Members.results,
            [12, 34], {}
        )
    
    @responses.activate
    def test_members_remove(self):
        self.assert_url_correct(
            responses.POST,
            r'{}/groups/\d+/members/\d+/remove'.format(config.API_URL),
            endpoint.Members.remove,
            [12, 34], {}
        )
    
    
      
    
if __name__ == '__main__':
    unittest.main()