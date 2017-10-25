import unittest
from unittest import mock

from groupy.api import images


class ImagesTests(unittest.TestCase):
    def setUp(self):
        self.m_session = mock.Mock()
        self.images = images.Images(self.m_session)


class UploadImageTests(ImagesTests):
    def setUp(self):
        super().setUp()
        self.m_session.post.return_value = mock.Mock(data={'payload': 'bar'})
        self.result = self.images.upload('foo')

    def test_result_is_payload(self):
        self.assertEqual(self.result, 'bar')


class DownloadImageTests(ImagesTests):
    def setUp(self):
        super().setUp()
        self.m_session.get.return_value = mock.Mock(content='bar')
        self.result = self.images.download('foo')

    def test_result_is_content(self):
        self.assertEqual(self.result, 'bar')
