import io
import unittest
from unittest import mock

from groupy.api import attachments


class ImagesTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.images = attachments.Images(self.m_session)


class UploadImageTests(ImagesTests):
    def setUp(self):
        super().setUp()
        self.m_session.post.return_value = mock.Mock(data={'url': 'bar'})
        self.result = self.images.upload(io.BytesIO(b'foo'))

    def test_result_is_payload(self):
        self.assertEqual(self.result, {'url': 'bar'})


class DownloadImageTests(ImagesTests):
    def setUp(self):
        super().setUp()
        self.m_session.get.return_value = mock.Mock(content='bar')
        m_image_attachment = mock.Mock(url='foo')
        self.result = self.images.download(m_image_attachment)

    def test_result_is_content(self):
        self.assertEqual(self.result, 'bar')
