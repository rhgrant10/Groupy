import unittest
from unittest import mock

from groupy.api import base


class MangerTests(unittest.TestCase):
    def setUp(self):
        self.manager = base.Manager(mock.Mock(), path='foo')

    def test_url_contains_path(self):
        self.assertEqual(self.manager.url, self.manager.base_url + 'foo')


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.data = {'foo': 'bar'}
        self.resource = base.Resource(**self.data)

    def test_data(self):
        self.assertEqual(self.data, self.resource.data)

    def test_data_access_via_resource_attributes(self):
        self.assertEqual(self.resource.foo, 'bar')

    def test_data_access_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.resource.baz
