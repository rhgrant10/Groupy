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
