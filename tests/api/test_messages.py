from unittest import mock
from datetime import datetime

from groupy import utils
from groupy.api import attachments
from groupy.api import messages
from . import base


class MessagesTests(base.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.messages = messages.Messages(self.m_session, group_id='bar')


class RawListMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_message_data()
        response = base.get_fake_response(data={'messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_messages(self):
        self.assertTrue(all(isinstance(m, messages.Message) for m in self.results))


class EmptyRawListMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_message_data()
        response = base.get_fake_response(code=304, data={'messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListModesMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        self.messages.list = mock.Mock()

    def test_before(self):
        self.messages.list_before('qux')
        self.messages.list.called_once_with(before_id='qux')

    def test_after(self):
        self.messages.list_after('qux')
        self.messages.list.called_once_with(after_id='qux')

    def test_since(self):
        self.messages.list_since('qux')
        self.messages.list.called_once_with(since_id='qux')


class CreateTextMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_message_data()
        response = base.get_fake_response(data={'message': message})
        self.m_session.post.return_value = response
        self.result = self.messages.create(text='qux')

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.Message))

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertEqual(message['text'], 'qux')

    def test_payload_lacks_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertNotIn('attachments', message)


class CreateAttachmentMessagesTests(MessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_message_data()
        response = base.get_fake_response(data={'message': message})
        self.m_session.post.return_value = response
        m_attachment = mock.Mock()
        m_attachment.to_json.return_value = {'qux': 'quux'}
        self.result = self.messages.create(attachments=[m_attachment])

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.Message))

    def test_payload_contains_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertEqual(message['attachments'], [{'qux': 'quux'}])

    def test_payload_lacks_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['message']
        self.assertNotIn('text', message)


class DirectMessagesTests(base.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.messages = messages.DirectMessages(self.m_session,
                                                other_user_id='foo')


class RawListDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_direct_message_data()
        response = base.get_fake_response(data={'direct_messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_direct_messages(self):
        self.assertTrue(all(isinstance(m, messages.DirectMessage) for m in self.results))


class EmptyRawListDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_direct_message_data()
        response = base.get_fake_response(code=304, data={'direct_messages': [message]})
        self.m_session.get.return_value = response
        self.results = self.messages._raw_list()

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListModesDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        self.messages.list = mock.Mock()

    def test_before(self):
        self.messages.list_before('qux')
        self.messages.list.called_once_with(before_id='qux')

    def test_since(self):
        self.messages.list_since('qux')
        self.messages.list.called_once_with(since_id='qux')


class CreateTextDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_direct_message_data()
        response = base.get_fake_response(data={'direct_message': message})
        self.m_session.post.return_value = response
        self.result = self.messages.create(text='qux')

    def test_result_is_message(self):
        self.assertTrue(isinstance(self.result, messages.DirectMessage))

    def test_payload_contains_text(self):
        __, kwargs = self.m_session.post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['direct_message']['text'], 'qux')

    def test_payload_lacks_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertNotIn('attachments', message)


class CreateAttachmentDirectMessagesTests(DirectMessagesTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_direct_message_data()
        response = base.get_fake_response(data={'direct_message': message})
        self.m_session.post.return_value = response
        m_attachment = mock.Mock()
        m_attachment.to_json.return_value = {'qux': 'quux'}
        self.result = self.messages.create(attachments=[m_attachment])

    def test_result_is_direct_message(self):
        self.assertTrue(isinstance(self.result, messages.DirectMessage))

    def test_payload_contains_attachments(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertEqual(message['attachments'], [{'qux': 'quux'}])

    def test_payload_lacks_text(self):
        __, kwargs = self.m_session.post.call_args
        message = kwargs['json']['direct_message']
        self.assertNotIn('text', message)


class GenericMessageTests(base.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = base.get_fake_generic_message_data(name='Alice', text='corge')
        self.message = messages.GenericMessage(self.m_manager, 'qux', **data)


class LikeGenericMessageTests(GenericMessageTests):
    def setUp(self):
        super().setUp()
        self.message._likes = mock.Mock()

    def test_like_uses_likes(self):
        self.message.like()
        self.assertTrue(self.message._likes.like.called)

    def test_unlike_uses_likes(self):
        self.message.unlike()
        self.assertTrue(self.message._likes.unlike.called)


class GenericMessageReprTests(GenericMessageTests):
    def test_repr(self):
        representation = repr(self.message)
        self.assertEqual(representation, "<GenericMessage(name='Alice', "
                                         "text='corge', attachments=0)>")


class MessageTests(base.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = base.get_fake_message_data()
        self.message = messages.Message(self.m_manager, **data)

    def test_conversation_id_is_group_id(self):
        self.assertEqual(self.message.conversation_id, self.message.group_id)


class DirectMessageTests(base.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()
        data = base.get_fake_direct_message_data()
        self.message = messages.DirectMessage(self.m_manager, **data)

    def test_conversation_id_is_sender_and_recipient(self):
        self.assertEqual(self.message.conversation_id, 'bar+baz')


class AttachmentTests(base.TestCase):
    def setUp(self):
        self.m_manager = mock.Mock()


class AttachmentToJsonTests(AttachmentTests):
    def test_json_is_correct(self):
        a = messages.Attachment(type='foo', text='bar')
        self.assertEqual(a.to_json(), {'type': 'foo', 'text': 'bar'})


class AttachmentsFromBulkDataTests(AttachmentTests):
    def setUp(self):
        super().setUp()
        self.data = [
            {'type': 'unknown', 'foo': 'bar'},
            {'type': 'location', 'lat': 4, 'lng': 2, 'name': 'baz'},
        ]
        self.attachments = attachments.Attachment.from_bulk_data(self.data)

    def test_attachment_one_is_attachment(self):
        self.assertEqual(type(self.attachments[0]), attachments.Attachment)

    def test_attachment_two_is_location(self):
        self.assertIsInstance(self.attachments[1], attachments.Location)


class LeaderboardTests(base.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.leaderboard = messages.Leaderboard(self.m_session, 'foo')


class LeaderboardGetMessagesTests(LeaderboardTests):
    def test_results_are_messages(self):
        message = base.get_fake_message_data()
        data = {'messages': [message]}
        self.m_session.get.return_value = base.get_fake_response(data=data)
        results = self.leaderboard._get_messages()
        self.assertTrue(all(isinstance(m, messages.Message) for m in results))


class LeaderboardListMethodTests(LeaderboardTests):
    def setUp(self):
        super().setUp()
        self.leaderboard._get_messages = mock.Mock()

    def test_period_is_day(self):
        self.leaderboard.list_day()
        self.assert_kwargs(self.leaderboard._get_messages, period='day')

    def test_period_is_week(self):
        self.leaderboard.list_week()
        self.assert_kwargs(self.leaderboard._get_messages, period='week')

    def test_period_is_month(self):
        self.leaderboard.list_month()
        self.assert_kwargs(self.leaderboard._get_messages, period='month')

    def test_path_is_mine(self):
        self.leaderboard.list_mine()
        self.assert_kwargs(self.leaderboard._get_messages, path='mine')

    def test_path_is_for_me(self):
        self.leaderboard.list_for_me()
        self.assert_kwargs(self.leaderboard._get_messages, path='for_me')


class LikesTests(base.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.likes = messages.Likes(self.m_session, conversation_id='foo',
                                    message_id='bar')


class LikeTests(LikesTests):
    def setUp(self):
        super().setUp()
        self.result = self.likes.like()

    def test_url_ends_with_like(self):
        (url,), __ = self.m_session.post.call_args
        self.assertTrue(url.endswith('/like'))

    def test_result_is_True(self):
        self.assertTrue(self.result)


class UnlikeTests(LikesTests):
    def setUp(self):
        super().setUp()
        self.result = self.likes.unlike()

    def test_url_ends_with_unlike(self):
        (url,), __ = self.m_session.post.call_args
        self.assertTrue(url.endswith('/unlike'))

    def test_result_is_True(self):
        self.assertTrue(self.result)


class GalleryTests(base.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.gallery = messages.Gallery(self.m_session, group_id='foo')


class RawListGalleryTests(GalleryTests):
    def setUp(self):
        super().setUp()
        message = base.get_fake_message_data()
        response = base.get_fake_response(data={'messages': [message]},
                                          code=self.code)
        self.m_session.get.return_value = response
        self.results = self.gallery._raw_list()


class NonemptyRawListGalleryTests(RawListGalleryTests):
    code = 200

    def test_results_are_messages(self):
        self.assertTrue(all(isinstance(m, messages.GenericMessage) for m in self.results))


class EmptyRawListGalleryTests(RawListGalleryTests):
    code = 304

    def test_results_are_empty(self):
        self.assertEqual(self.results, [])


class ListMethodGalleryTests(GalleryTests):
    def setUp(self):
        super().setUp()
        self.gallery._raw_list = mock.Mock()
        self.when = datetime.now()
        self.ts = utils.get_rfc3339(self.when)

    def test_before(self):
        self.gallery.list_before(self.when)
        self.assert_kwargs(self.gallery._raw_list, before=self.ts)

    def test_since(self):
        self.gallery.list_since(self.when)
        self.assert_kwargs(self.gallery._raw_list, since=self.ts)

    def test_after(self):
        self.gallery.list_after(self.when)
        self.assert_kwargs(self.gallery._raw_list, after=self.ts)
