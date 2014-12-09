from .. import endpoint
from .. import errors
from ... import config

import unittest
import requests
import responses
import json
import re
import urllib
import builtins
from mock import mock_open, patch

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
            endpoint.Groups.index,
                page=12, per_page=34
        )
    
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
        self.assert_url_correct(responses.POST,
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
    
    
if __name__ == '__main__':
    unittest.main()