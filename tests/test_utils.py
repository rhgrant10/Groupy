import unittest
from unittest import mock

from groupy import utils
from groupy import exceptions


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


class FilterTests(unittest.TestCase):
    def setUp(self):
        self.objects = [
            mock.Mock(foo='foo', baz=0),
            mock.Mock(foo='bar', baz=1),
            mock.Mock(foo='baz', baz=2),
            mock.Mock(foo='qux', baz=3),
        ]

    def test_find(self):
        f = utils.make_filter(foo__gt='foo')
        match = f.find(self.objects)
        self.assertEqual(match, self.objects[3])

    def test_filter(self):
        f = utils.make_filter(baz__gt=1)
        matches = list(f(self.objects))
        self.assertEqual(matches, self.objects[2:4])

    def test_no_matches(self):
        f = utils.make_filter(foobar='barfoo')
        with self.assertRaises(exceptions.NoMatchesError):
            f.find(self.objects)

    def test_multiple_matches(self):
        f = utils.make_filter(baz__lt=10)
        with self.assertRaises(exceptions.MultipleMatchesError):
            f.find(self.objects)
