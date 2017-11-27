import unittest
from unittest import mock

from groupy import pagers


class PagerTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        self.m_endpoint = mock.Mock()
        self.m_endpoint.side_effect = ['abc', 'xyz']
        self.params = {'x': 42}
        self.pager = pagers.Pager(self.m_manager, self.m_endpoint, **self.params)

    def test_iterates_over_current_page_items(self):
        items = list(self.pager)
        self.assertEqual(items, list('abc'))

    def test_autopage_iterates_over_items_from_all_pages(self):
        self.pager.set_next_page_params = mock.Mock()
        items = list(self.pager.autopage())
        self.assertEqual(items, list('abcxyz'))

    def test_params_passed(self):
        __, kwargs = self.m_endpoint.call_args
        self.assertEqual(kwargs.get('x'), 42)

    def test_set_next_page_params_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.pager.set_next_page_params()

    def test_current_page_items_are_indexable(self):
        self.assertEqual(self.pager[0], 'a')


class GroupListTests(unittest.TestCase):
    def setUp(self):
        m_manager = mock.Mock()
        m_endpoint = mock.Mock()
        self.groups = pagers.GroupList(m_manager, m_endpoint)
        self.page = self.groups.params['page']

    def test_next_page_params_advances_page_by_one(self):
        self.groups.set_next_page_params()
        self.assertEqual(self.groups.params['page'], self.page + 1)


class MessageListModeDetectionTests(unittest.TestCase):
    def test_default_mode_is_before_id(self):
        mode = pagers.MessageList.detect_mode()
        self.assertEqual(mode, 'before_id')

    def test_before_mode(self):
        mode = pagers.MessageList.detect_mode(before_id='x')
        self.assertEqual(mode, 'before_id')

    def test_after_mode(self):
        mode = pagers.MessageList.detect_mode(after_id='x')
        self.assertEqual(mode, 'after_id')

    def test_since_mode(self):
        mode = pagers.MessageList.detect_mode(since_id='x')
        self.assertEqual(mode, 'since_id')

    def test_ambiguous_mode(self):
        with self.assertRaises(ValueError):
            pagers.MessageList.detect_mode(since_id='x', before_id='y')


class MessageListTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        self.m_endpoint = mock.Mock()
        pages = [
            [mock.Mock(id='foo'), mock.Mock(id='bar')],
            [mock.Mock(id='baz'), mock.Mock(id='qux')],
        ]
        self.m_endpoint.side_effect = pages
        self.messages = pagers.MessageList(self.m_manager, self.m_endpoint)

    def test_next_page_params_advances_page_by_one(self):
        self.messages.set_next_page_params()
        self.assertEqual(self.messages.params['before_id'], 'bar')
