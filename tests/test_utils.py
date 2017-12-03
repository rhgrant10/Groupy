import unittest

from groupy import utils


class UrlJoinTests(unittest.TestCase):
    url = 'http://example.com/foo'

    def test_result_is_base_when_no_path(self):
        self.assertEqual(utils.urljoin(self.url), self.url)

    def test_path_appending(self):
        url = utils.urljoin(self.url, 'bar')
        self.assertEqual(url, 'http://example.com/foo/bar')


class TrailingSlashUrlJoinTests(UrlJoinTests):
    url = 'http://example.com/foo/'


class ParseShareUrlTests(unittest.TestCase):
    url = 'http://example.com/foo/group_id/share_token'

    def setUp(self):
        self.group_id, self.share_token = utils.parse_share_url(self.url)

    def test_group_id_is_correct(self):
        self.assertEqual(self.group_id, 'group_id')

    def test_share_token_is_correct(self):
        self.assertEqual(self.share_token, 'share_token')


class TrailingSlashParseShareUrlTests(ParseShareUrlTests):
    url = 'http://example.com/foo/group_id/share_token/'
