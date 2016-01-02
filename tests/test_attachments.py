"""
.. module:: test_attachments

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

Unit tests for the attachments module.

"""
import unittest
from unittest import mock

from groupy.object import attachments


class AttachmentAsDictTests(unittest.TestCase):
    def test_attachment_as_dict(self):
        dict_ = attachments.Attachment('thetype').as_dict()
        self.assertEqual(dict_, {'type': 'thetype'})


class GenericAttachmentTests(unittest.TestCase):
    def test_all_kwargs_become_instance_attributes(self):
        attachment = attachments.GenericAttachment('thetype', x=5)
        self.assertEqual(attachment.x, 5)

    def test_impossible_attribute_names_are_accepted(self):
        attachment = attachments.GenericAttachment('thetype', **{'A B': 5})
        self.assertEqual(getattr(attachment, 'A B'), 5)


class ImageAttachmentTests(unittest.TestCase):
    def test_type_is_image(self):
        image = attachments.Image('url')
        self.assertEqual(image.type, 'image')

    def test_source_url_defaults_to_None(self):
        image = attachments.Image('url')
        self.assertIsNone(image.source_url)

    def test_repr_contains_repr_of_url(self):
        image = attachments.Image('url')
        self.assertIn(repr('url'), repr(image))


class ImageAttachmentFromFileTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Images')
    def setUp(self, MockImageEndpoint):
        self.MockImageEndpoint = MockImageEndpoint
        attachments.Image.file('image')

    def test_image_create_endpoint_called_once(self):
        self.assertEqual(self.MockImageEndpoint.create.call_count, 1)

    def test_image_create_endpoint_called_with_input_image(self):
        self.assertEqual(self.MockImageEndpoint.create.call_args[0],
                         ('image',))


class ImageAttachmentDownloadTests(unittest.TestCase):
    @mock.patch('groupy.api.endpoint.Images')
    def setUp(self, MockImageEndpoint):
        self.MockImageEndpoint = MockImageEndpoint
        attachment = attachments.Image('url')
        attachment.download()

    def test_image_download_endpoint_called_once(self):
        self.assertEqual(self.MockImageEndpoint.download.call_count, 1)

    def test_image_download_endpoint_called_once_with_image_url(self):
        self.assertEqual(self.MockImageEndpoint.download.call_args[0],
                         ('url',))


class LocationAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.location = attachments.Location('name', 'lat', 'lng')

    def test_foursquare_venue_id_defaults_to_None(self):
        self.assertIsNone(self.location.foursquare_venue_id)

    def test_type_is_location(self):
        self.assertEqual(self.location.type, 'location')

    def test_repr_contains_repr_of_name(self):
        self.assertIn(repr('name'), repr(self.location))

    def test_repr_contains_repr_of_latitude(self):
        self.assertIn(repr('lat'), repr(self.location))

    def test_repr_contains_repr_of_longitude(self):
        self.assertIn(repr('lng'), repr(self.location))


class EmojiAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.emoji = attachments.Emoji('placeholder', 'charmap')

    def test_type_is_emoji(self):
        self.assertEqual(self.emoji.type, 'emoji')

    def test_repr_contains_repr_of_placeholder(self):
        self.assertIn(repr('placeholder'), repr(self.emoji))

    def test_repr_contains_repr_of_charmap(self):
        self.assertIn(repr('charmap'), repr(self.emoji))


class SplitAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.split = attachments.Split('token')

    def test_type_is_split(self):
        self.assertEqual(self.split.type, 'split')

    def test_repr_contains_repr_of_token(self):
        self.assertIn(repr('token'), repr(self.split))


class MentionsAttachmentTests(unittest.TestCase):
    def setUp(self):
        self.mentions = attachments.Mentions('user_ids')

    def test_repr_contains_repr_of_user_ids(self):
        self.assertIn(repr('user_ids'), repr(self.mentions))


class AttachmentFactoryTests(unittest.TestCase):
    def test_image_factory(self):
        data = {'type': 'image', 'url': 'url'}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'image')

    def test_location_factory(self):
        data = {'type': 'location', 'name': 'n', 'lat': 't', 'lng': 'g'}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'location')

    def test_emoji_factory(self):
        data = {'type': 'emoji', 'placeholder': 'p', 'charmap': 'c'}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'emoji')

    def test_mentions_factory(self):
        data = {'type': 'mentions', 'user_ids': 'p'}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'mentions')

    def test_split_factory(self):
        data = {'type': 'split', 'token': 't'}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'split')

    def test_generic_factory(self):
        data = {'type': 'whoknows', 'x': 5}
        attachment = attachments.AttachmentFactory.create(**data)
        self.assertEqual(attachment.type, 'whoknows')
