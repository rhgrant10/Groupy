import unittest

from groupy.api import attachments


class TestAttachmentsFromData(unittest.TestCase):
    def test_known_attachment_type(self):
        data = {'type': 'split', 'token': 'foo'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Split)

    def test_unknown_attachment_type(self):
        data = {'type': 'foo', 'bar': 'baz'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Attachment)

    def test_known_attachment_type_with_unknown_field(self):
        data = {'type': 'split', 'token': 'foo', 'unknown': 'field'}
        with self.assertRaises(TypeError):
            attachments.Attachment.from_data(**data)
