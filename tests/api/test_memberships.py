from unittest import mock

from groupy.api import memberships
from groupy.exceptions import ResultsNotReady
from groupy.exceptions import ResultsExpired
from .base import get_fake_response, get_fake_member_data
from .base import TestCase


class MembershipsTests(TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.memberships = memberships.Memberships(self.m_session,
                                                   group_id='foo')


class AddMembershipTests(MembershipsTests):
    def setUp(self):
        super().setUp()
        self.members = [{'bar': 'baz'}, {'baz': 'qux'}]
        self.m_session.post.return_value = get_fake_response(data={'qux': 'quux'})
        self.result = self.memberships.add(*self.members)

    def test_result_is_MembershipRequest(self):
        self.assertIsInstance(self.result, memberships.MembershipRequest)

    def test_payload_contained_guids(self):
        __, kwargs = self.m_session.post.call_args
        for member in kwargs['json']['members']:
            with self.subTest(member=member):
                self.assertIn('guid', member)


class CheckMembershipTests(MembershipsTests):
    def test_results_not_ready_yet(self):
        self.m_session.get.return_value = get_fake_response(code=503)
        with self.assertRaises(ResultsNotReady):
            self.memberships.check('bar')

    def test_results_expired(self):
        self.m_session.get.return_value = get_fake_response(code=404)
        with self.assertRaises(ResultsExpired):
            self.memberships.check('bar')

    def test_results_available(self):
        data = {'members': [{'baz': 'qux'}]}
        self.m_session.get.return_value = get_fake_response(data=data)
        result = self.memberships.check('bar')
        self.assertEqual(result, data['members'])


class RemoveMembershipTests(MembershipsTests):
    def test_result_is_True(self):
        self.m_session.post.return_value = mock.Mock(ok=True)
        self.assertTrue(self.memberships.remove('bar'))


class MemberTests(TestCase):
    @mock.patch('groupy.api.memberships.Memberships')
    @mock.patch('groupy.api.memberships.user')
    def setUp(self, *__):
        self.m_manager = mock.Mock()
        self.data = get_fake_member_data(group_id='foo_group_id')
        self.member = memberships.Member(self.m_manager, **self.data)
        self._blocks = self.member._user.blocks
        self._memberships = self.member._memberships


class MemberIsBlockedTests(MemberTests):
    def setUp(self):
        super().setUp()
        self.member.is_blocked()

    def test_uses_user_id(self):
        self.assert_kwargs(self._blocks.between,
                           other_user_id=self.data['user_id'])


class BlockMemberTests(MemberTests):
    def setUp(self):
        super().setUp()
        self.member.block()

    def test_uses_user_id(self):
        self.assert_kwargs(self._blocks.block,
                           other_user_id=self.data['user_id'])


class UnblockMemberTests(MemberTests):
    def setUp(self):
        super().setUp()
        self.member.unblock()

    def test_uses_user_id(self):
        self.assert_kwargs(self._blocks.unblock,
                           other_user_id=self.data['user_id'])


class RemoveMemberTests(MemberTests):
    def setUp(self):
        super().setUp()
        self.member.remove()

    def test_uses_user_id(self):
        self.assert_kwargs(self.member._memberships.remove,
                           membership_id=self.data['id'])


class MembershipRequestTests(TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        self.requests = [get_fake_member_data(guid='foo-%s' % n) for n in range(2)]
        self.request = memberships.MembershipRequest(self.m_manager,
                                                     *self.requests,
                                                     group_id='baz',
                                                     results_id='bar')


class ReadyResultsTests(MembershipRequestTests):
    def setUp(self):
        super().setUp()
        self.m_manager.check.return_value = self.requests
        self.is_ready = self.request.is_ready()
        self.results = self.request.get()

    def test_result_is_ready(self):
        self.assertTrue(self.is_ready)

    def test_results_are_members(self):
        for member in self.results.members:
            with self.subTest(member=member):
                self.assertIsInstance(member, memberships.Member)

    def test_there_are_no_failures(self):
        self.assertEqual(self.results.failures, [])

    def test_resulting_members_have_no_guids(self):
        for member in self.results.members:
            with self.subTest(member=member):
                with self.assertRaises(AttributeError):
                    member.guid


class NotReadyResultsTests(MembershipRequestTests):
    def setUp(self):
        super().setUp()
        self.m_manager.check.side_effect = ResultsNotReady(response=None)
        self.is_ready = self.request.is_ready()

    def test_result_is_not_ready(self):
        self.assertFalse(self.is_ready)

    def test_getting_result_raises_not_ready_exception(self):
        with self.assertRaises(ResultsNotReady):
            self.request.get()


class ExpiredResultsTests(MembershipRequestTests):
    def setUp(self):
        super().setUp()
        self.m_manager.check.side_effect = ResultsExpired(response=None)
        self.is_ready = self.request.is_ready()

    def test_result_is_ready(self):
        self.assertTrue(self.is_ready)

    def test_getting_result_raises_expired_exception(self):
        with self.assertRaises(ResultsExpired):
            self.request.get()


class FailureResultsTests(MembershipRequestTests):
    def setUp(self):
        super().setUp()
        self.m_manager.check.return_value = self.requests[1:]
        self.is_ready = self.request.is_ready()
        self.results = self.request.get()

    def test_not_all_requests_have_results(self):
        self.assertNotEqual(len(self.results.members), len(self.requests))

    def test_there_are_failures(self):
        self.assertTrue(self.results.failures)

    def test_the_failure_is_the_correct_request(self):
        self.assertEqual(self.results.failures, self.requests[:1])


class PollResultsTests(MembershipRequestTests):
    def setUp(self):
        super().setUp()
        self.request.get = mock.Mock()
        self.request.is_ready = mock.Mock()
        self.request.is_ready.side_effect = [False, True]
        self.result = self.request.poll(interval=0)

    def test_result_is_get(self):
        self.assertEqual(self.result, self.request.get.return_value)
