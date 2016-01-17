"""
.. module:: test_listers

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

Unit tests for the listers module.

"""
import unittest

from groupy.object import listers
from groupy.api import errors


class Container:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


class EmptyFilterListTests(unittest.TestCase):
    def setUp(self):
        self.flist = listers.FilterList()

    def test_first_is_None(self):
        self.assertIsNone(self.flist.first)

    def test_last_is_None(self):
        self.assertIsNone(self.flist.last)

    def test_length_is_zero(self):
        self.assertEqual(len(self.flist), 0)


class FilterListTests(unittest.TestCase):
    def setUp(self):
        self.data = [Container(x) for x in ('a', 'aa', 'b')]
        self.flist = listers.FilterList(self.data)

    def test_operator_chosen_by_name(self):
        result = self.flist.filter(value__lt='aa')
        self.assertEqual(list(result), [Container('a')])

    def test_invalid_operator_raises_InvalidOperatorError(self):
        with self.assertRaises(errors.InvalidOperatorError):
            self.flist.filter(value__wat='huh?')

    def test_default_operator_is_equality(self):
        result = self.flist.filter(value='aa')
        self.assertEqual(list(result), [Container('aa')])

    def test_first_is_first(self):
        self.assertEqual(self.flist.first, self.data[0])

    def test_last_is_last(self):
        self.assertEqual(self.flist.last, self.data[-1])
