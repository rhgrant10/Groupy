"""
.. module:: test_listers

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

Unit tests for the listers module.

"""
import unittest
from unittest import mock
from groupy.object import listers


class Spec(object):
    x = None


class EmptyFilterListTests(unittest.TestCase):
    def setUp(self):
        self.data = []
        self.flist = listers.FilterList(self.data)

    def test_first_is_None(self):
        self.assertTrue(self.flist.first is None)

    def test_last_is_None(self):
        self.assertTrue(self.flist.last is None)

    def test_length_is_zero(self):
        self.assertTrue(len(self.flist) == 0)


class NumericFilterTests(unittest.TestCase):
    def setUp(self):
        self.data = [mock.MagicMock(spec=Spec, x=x) for x in range(-2, 3)]
        self.flist = listers.FilterList(self.data)

    # Less than
    def test_x_less_than_least(self):
        self.assertTrue(list(self.flist.filter(x__lt=-2)) == [])

    def test_x_less_than_negative(self):
        self.assertTrue(list(self.flist.filter(x__lt=-1)) == self.data[:1])

    def test_x_less_than_zero(self):
        self.assertTrue(list(self.flist.filter(x__lt=0)) == self.data[:2])

    def test_x_less_than_positive(self):
        self.assertTrue(list(self.flist.filter(x__lt=1)) == self.data[:3])

    def test_x_less_than_greatest(self):
        self.assertTrue(list(self.flist.filter(x__lt=2)) == self.data[:4])

    def test_y_less_than_least(self):
        self.assertTrue(list(self.flist.filter(y__lt=-2)) == [])

    def test_y_less_than_negative(self):
        self.assertTrue(list(self.flist.filter(y__lt=-1)) == [])

    def test_y_less_than_zero(self):
        self.assertTrue(list(self.flist.filter(y__lt=0)) == [])

    def test_y_less_than_positive(self):
        self.assertTrue(list(self.flist.filter(y__lt=1)) == [])

    def test_y_less_than_greatest(self):
        self.assertTrue(list(self.flist.filter(y__lt=2)) == [])

    # Greater than
    def test_x_greater_than_least(self):
        self.assertTrue(list(self.flist.filter(x__gt=-2)) == self.data[1:])

    def test_x_greater_than_negative(self):
        self.assertTrue(list(self.flist.filter(x__gt=-1)) == self.data[2:])

    def test_x_greater_than_zero(self):
        self.assertTrue(list(self.flist.filter(x__gt=0)) == self.data[3:])

    def test_x_greater_than_positive(self):
        self.assertTrue(list(self.flist.filter(x__gt=1)) == self.data[4:])

    def test_x_greater_than_greatest(self):
        self.assertTrue(list(self.flist.filter(x__gt=2)) == [])

    def test_y_greater_than_least(self):
        self.assertTrue(list(self.flist.filter(y__gt=-2)) == [])

    def test_y_greater_than_negative(self):
        self.assertTrue(list(self.flist.filter(y__gt=-1)) == [])

    def test_y_greater_than_zero(self):
        self.assertTrue(list(self.flist.filter(y__gt=0)) == [])

    def test_y_greater_than_positive(self):
        self.assertTrue(list(self.flist.filter(y__gt=1)) == [])

    def test_y_greater_than_greatest(self):
        self.assertTrue(list(self.flist.filter(y__gt=2)) == [])

    # Less than or equal
    def test_x_less_than_or_equal_least(self):
        self.assertTrue(list(self.flist.filter(x__le=-2)) == self.data[:1])

    def test_x_less_than_or_equal_negative(self):
        self.assertTrue(list(self.flist.filter(x__le=-1)) == self.data[:2])

    def test_x_less_than_or_equal_zero(self):
        self.assertTrue(list(self.flist.filter(x__le=0)) == self.data[:3])

    def test_x_less_than_or_equal_positive(self):
        self.assertTrue(list(self.flist.filter(x__le=1)) == self.data[:4])

    def test_x_less_than_or_equal_greatest(self):
        self.assertTrue(list(self.flist.filter(x__le=2)) == self.data)

    def test_y_less_than_or_equal_least(self):
        self.assertTrue(list(self.flist.filter(y__le=-2)) == [])

    def test_y_less_than_or_equal_negative(self):
        self.assertTrue(list(self.flist.filter(y__le=-1)) == [])

    def test_y_less_than_or_equal_zero(self):
        self.assertTrue(list(self.flist.filter(y__le=0)) == [])

    def test_y_less_than_or_equal_positive(self):
        self.assertTrue(list(self.flist.filter(y__le=1)) == [])

    def test_y_less_than_or_equal_greatest(self):
        self.assertTrue(list(self.flist.filter(y__le=2)) == [])

    # Greater than or equal
    def test_x_greater_than_or_equal_least(self):
        self.assertTrue(list(self.flist.filter(x__ge=-2)) == self.data)

    def test_x_greater_than_or_equal_negative(self):
        self.assertTrue(list(self.flist.filter(x__ge=-1)) == self.data[1:])

    def test_x_greater_than_or_equal_zero(self):
        self.assertTrue(list(self.flist.filter(x__ge=0)) == self.data[2:])

    def test_x_greater_than_or_equal_positive(self):
        self.assertTrue(list(self.flist.filter(x__ge=1)) == self.data[3:])

    def test_x_greater_than_or_equal_greatest(self):
        self.assertTrue(list(self.flist.filter(x__ge=2)) == self.data[4:])

    def test_y_greater_than_or_equal_least(self):
        self.assertTrue(list(self.flist.filter(y__ge=-2)) == [])

    def test_y_greater_than_or_equal_negative(self):
        self.assertTrue(list(self.flist.filter(y__ge=-1)) == [])

    def test_y_greater_than_or_equal_zero(self):
        self.assertTrue(list(self.flist.filter(y__ge=0)) == [])

    def test_y_greater_than_or_equal_positive(self):
        self.assertTrue(list(self.flist.filter(y__ge=1)) == [])

    def test_y_greater_than_or_equal_greatest(self):
        self.assertTrue(list(self.flist.filter(y__ge=2)) == [])


class StringFilterTests(unittest.TestCase):
    def setUp(self):
        self.strings = ('', 'abc', '123', 'abc123')
        self.data = [mock.MagicMock(spec=Spec, x=x) for x in self.strings]
        self.flist = listers.FilterList(self.data)

    # Contains
    def test_x_contains_empty_string(self):
        self.assertTrue(list(self.flist.filter(x__contains='')) == self.data)

    def test_x_contains_missing(self):
        self.assertTrue(list(self.flist.filter(x__contains='xyz')) == [])

    def test_x_contains_present(self):
        self.assertTrue(list(self.flist.filter(x__contains='abc')) == self.data[1::2])

    def test_y_contains_present(self):
        self.assertTrue(list(self.flist.filter(y__contains='abc')) == [])

    def test_y_contains_empty_string(self):
        self.assertTrue(list(self.flist.filter(y__contains='')) == [])

    # Equal


    # Not Equal
