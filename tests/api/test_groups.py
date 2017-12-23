from unittest import mock

from .base import get_fake_response, get_fake_member_data, get_fake_group_data
from .base import TestCase
from groupy import pagers
from groupy.api import groups


class GroupsTests(TestCase):
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

    def test_results_is_a_list(self):
        self.assertTrue(isinstance(self.results, list))


class ListCurrentGroupsTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group = get_fake_group_data()
        response = get_fake_response(data=[group])
        self.m_session.get.return_value = response
        self.results = self.groups.list()

    def test_results_is_a_GroupList(self):
        self.assertTrue(isinstance(self.results, pagers.GroupList))


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
        response = get_fake_response(data={'group': group})
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


class ChangeOwnersGroupTests(GroupsTests):
    def setUp(self):
        super().setUp()
        group_id = 'foo'
        owner_id = 'bar'
        result = {'group_id': group_id, 'owner_id': owner_id, 'status': '200'}
        response = get_fake_response(data={'results': [result]})
        self.m_session.post.return_value = response
        self.result = self.groups.change_owners(group_id='foo', owner_id='bar')

    def test_result_is_change_owners_result(self):
        self.assertTrue(isinstance(self.result, groups.ChangeOwnersResult))


class GroupTests(TestCase):
    def setUp(self):
        self.group = groups.Group(mock.Mock(), **get_fake_group_data())


class GroupEqualityTests(GroupTests):
    def test_same_group_id(self):
        group = groups.Group(mock.Mock(), **get_fake_group_data())
        self.assertEqual(self.group, group)

    def test_different_group_id(self):
        group = groups.Group(mock.Mock(), **get_fake_group_data())
        group.group_id = 2 * self.group.group_id
        self.assertNotEqual(self.group, group)


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
        self.members = [get_fake_member_data(), get_fake_member_data()]
        refreshed_group = get_fake_group_data(name='qux', members=self.members)
        self.group.manager.get.return_value = get_fake_response(data=refreshed_group)
        self.group.refresh_from_server()

    def test_manager_used(self):
        self.assertTrue(self.group.manager.get.called)

    def test_name_is_updated(self):
        self.assertEqual(self.group.name, 'qux')

    def test_members_is_updated(self):
        self.assertEqual(len(self.group.members), len(self.members))


class UnsuccessfulChangeOwnersResultTests(TestCase):
    known_codes = '400', '403', '404', '405'

    def test_is_not_success(self):
        for code in self.known_codes:
            with self.subTest(code=code):
                result = groups.ChangeOwnersResult('foo', 'bar', code)
                self.assertFalse(result.is_success)

    def test_is_falsey(self):
        for code in self.known_codes:
            with self.subTest(code=code):
                result = groups.ChangeOwnersResult('foo', 'bar', code)
                self.assertFalse(result)

    def test_reason_is_not_unknown(self):
        for code in self.known_codes:
            with self.subTest(code=code):
                result = groups.ChangeOwnersResult('foo', 'bar', code)
                self.assertNotEqual(result.reason, 'unknown')


class UnknownChangeOwnerResults(TestCase):
    def setUp(self):
        self.result = groups.ChangeOwnersResult('foo', 'bar', '419')

    def test_is_not_success(self):
        self.assertFalse(self.result.is_success)

    def test_is_falsey(self):
        self.assertFalse(self.result)

    def test_reason_is_unknown(self):
        self.assertEqual(self.result.reason, 'unknown')
