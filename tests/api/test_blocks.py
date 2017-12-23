import unittest
from unittest import mock

from groupy.api import blocks


class BlocksTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.user_id = 'foo'
        self.blocks = blocks.Blocks(self.m_session, self.user_id)


class BlocksListTests(BlocksTests):
    def setUp(self):
        super().setUp()
        data = {'blocks': [{'x': 'X'}, {'y': 'Y'}]}
        self.m_session.get.return_value = mock.Mock(data=data)
        self.results = self.blocks.list()

    def test_result_is_blocks(self):
        self.assertTrue(all(isinstance(b, blocks.Block) for b in self.results))

    def test_user_id_is_in_params(self):
        __, kwargs = self.m_session.get.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('user'), self.user_id)


class BlocksBetweenTests(BlocksTests):
    def setUp(self):
        super().setUp()
        data = {'between': True}
        self.m_session.get.return_value = mock.Mock(data=data)
        self.other_user_id = 'qux'
        self.result = self.blocks.between(other_user_id=self.other_user_id)

    def test_result_is_True(self):
        self.assertTrue(self.result)

    def test_user_id_is_in_params(self):
        __, kwargs = self.m_session.get.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('user'), self.user_id)

    def test_other_user_id_is_in_params(self):
        __, kwargs = self.m_session.get.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('otherUser'), self.other_user_id)


class BlocksBlockTests(BlocksTests):
    def setUp(self):
        super().setUp()
        data = {'block': {'x': 'X'}}
        self.m_session.post.return_value = mock.Mock(data=data)
        self.other_user_id = 'qux'
        self.result = self.blocks.block(other_user_id=self.other_user_id)

    def test_result_is_block(self):
        self.assertTrue(isinstance(self.result, blocks.Block))

    def test_user_id_is_in_params(self):
        __, kwargs = self.m_session.post.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('user'), self.user_id)

    def test_other_user_id_is_in_params(self):
        __, kwargs = self.m_session.post.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('otherUser'), self.other_user_id)


class BlocksUnblockTests(BlocksTests):
    def setUp(self):
        super().setUp()
        self.m_session.delete.return_value = mock.Mock(ok=True)
        self.other_user_id = 'qux'
        self.result = self.blocks.unblock(other_user_id=self.other_user_id)

    def test_result_is_True(self):
        self.assertTrue(self.result)

    def test_user_id_is_in_params(self):
        __, kwargs = self.m_session.delete.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('user'), self.user_id)

    def test_other_user_id_is_in_params(self):
        __, kwargs = self.m_session.delete.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params.get('otherUser'), self.other_user_id)


class BlockTests(unittest.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        self.block = blocks.Block(self.m_manager, user_id='foo',
                                  blocked_user_id='bar')


class MiscBlockTests(BlockTests):
    def test_repr_contains_pertinent_info(self):
        representation = "<Block(blocked_user_id='bar')>"
        self.assertEqual(representation, repr(self.block))

    def test_exists_uses_blocks_between(self):
        self.block.exists()
        self.assertTrue(self.m_manager.between.called)

    def test_unblock_uses_unblock(self):
        self.block.unblock()
        self.assertTrue(self.m_manager.unblock.called)


class BlockEqualityTests(BlockTests):
    def test_different_blocked_user_id(self):
        block = blocks.Block(self.m_manager, user_id=self.block.user_id,
                             blocked_user_id='qux')
        self.assertNotEqual(self.block, block)

    def test_different_user_id(self):
        block = blocks.Block(self.m_manager, user_id='qux',
                             blocked_user_id=self.block.blocked_user_id)
        self.assertNotEqual(self.block, block)

    def test_same_user_id_and_blocked_user_id(self):
        block = blocks.Block(self.m_manager, user_id=self.block.user_id,
                             blocked_user_id=self.block.blocked_user_id)
        self.assertEqual(self.block, block)
