import unittest
from unittest import mock

from groupy.api import groups
from .base import get_fake_response


def get_fake_group_data(**kwargs):
    group_data = {
        'id': 'foo',
        'name': 'foobar',
        'group_id': 'bar',
        'created_at': 1302623328,
        'updated_at': 1302623329,
    }
    group_data.update(kwargs)
    return group_data


class GroupsTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.groups = groups.Groups(self.m_session)


class RawListGroupsTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=[group])
        self.m_session.get.return_value = response
        self.results = self.groups._raw_list(x='X')

    def test_params(self):
        __, kwargs = self.m_session.get.call_args
        params = kwargs.get('params') or {}
        self.assertEqual(params, {'x': 'X'})

    def test_results_are_groups(self):
        self.assertTrue(all(isinstance(g, groups.Group) for g in self.results))


class EmptyRawListGroupsTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=[group], code=304)
        self.m_session.get.return_value = response
        self.results = self.groups._raw_list()

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListFormerGroupsTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=[group])
        self.m_session.get.return_value = response
        self.results = self.groups.list_former()

    def test_results_are_groups(self):
        self.assertTrue(all(isinstance(g, groups.Group) for g in self.results))


class GetGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=group)
        self.m_session.get.return_value = response
        self.result = self.groups.get('foo')

    def test_result_is_group(self):
        self.assertTrue(isinstance(self.result, groups.Group))


class CreateGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=group)
        self.m_session.post.return_value = response
        self.result = self.groups.create(name='foo')

    def test_result_is_group(self):
        self.assertTrue(isinstance(self.result, groups.Group))


class UpdateGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=group)
        self.m_session.post.return_value = response
        self.result = self.groups.update('foo', name='bar')

    def test_result_is_group(self):
        self.assertTrue(isinstance(self.result, groups.Group))


class DestroyGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        self.m_session.post.return_value = mock.Mock(ok=True)
        self.result = self.groups.destroy('foo')

    def test_result_is_True(self):
        self.assertTrue(self.result)


class JoinGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=group)
        self.m_session.post.return_value = response
        self.result = self.groups.join(group_id='foo', share_token='bar')

    def test_result_is_group(self):
        self.assertTrue(isinstance(self.result, groups.Group))


class RejoinGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=group)
        self.m_session.post.return_value = response
        self.result = self.groups.rejoin(group_id='foo')

    def test_result_is_group(self):
        self.assertTrue(isinstance(self.result, groups.Group))


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.group = groups.Group(mock.Mock(), **get_fake_group_data())


class GroupReprTests(GroupTests):
    def test_repr(self):
        representation = repr(self.group)
        self.assertEqual(representation, "<Group(name='foobar')>")


class GroupPostTests(GroupTests):
    def setUp(self):
        super().setUp()
        self.group.messages = mock.Mock()
        self.result = self.group.post(text='foo')

    def test_messages_used(self):
        self.assertTrue(self.group.messages.create.called)


class GroupUpdateTests(GroupTests):
    def setUp(self):
        super().setUp()
        self.group.update(name='foowho')

    def test_manager_used(self):
        self.assertTrue(self.group.manager.update.called)


class GroupDestroyTests(GroupTests):
    def setUp(self):
        super().setUp()
        self.group.destroy()

    def test_manager_used(self):
        self.assertTrue(self.group.manager.destroy.called)


class GroupRejoinTests(GroupTests):
    def setUp(self):
        super().setUp()
        self.group.rejoin()

    def test_manager_used(self):
        self.assertTrue(self.group.manager.rejoin.called)


class GroupRefreshFromServerTests(GroupTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data(name='qux')
        self.group.manager.get.return_value = get_fake_response(data=group)
        self.group.refresh_from_server()

    def test_manager_used(self):
        self.assertTrue(self.group.manager.get.called)

    def test_name_is_updated(self):
        self.assertEqual(self.group.name, 'qux')


class GroupHasOmissionTests(GroupTests):
    def test_present(self):
        self.assertFalse(self.group.has_omission('group_id'))

    def test_omitted(self):
        self.assertTrue(self.group.has_omission('members'))

    def test_no_omission(self):
        self.assertFalse(self.group.has_omission('corge'))
