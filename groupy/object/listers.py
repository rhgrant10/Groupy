"""
.. module:: listers
    :platform: Unix, Windows
    :synopsis: A module containing classes used for lists of objects

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

This module contains classes that provide filterable lists and message pagers.

"""
import operator

from ..api import errors


class FilterList(list):
    """A filterable list.

    Acts just like a regular :class:`list`, except it can be filtered using a
    special keyword syntax. Also, the first and last items are special
    properties.
    """
    def filter(self, **kwargs):
        """Filter the list and return a new instance.

        Arguments are keyword arguments only, and can be appended with
        operator method names to indicate relationships other than equals.
        For example, to filter the list down to only items whose ``name``
        property contains "ie":

        .. code-block:: python

            new_list = filter_list.filter(name__contains='ie')

        As another example, this filters the list down to only those
        with a ``created`` property that is less than 1234567890:

        .. code-block:: python

            new_list = filter_list.filter(created__lt=1234567890)

        Acceptable operators are:

        - ``__lt``: less than
        - ``__gt``: greater than
        - ``__contains``: contains
        - ``__eq``: equal to
        - ``__ne``: not equal to
        - ``__le``: less than or equal to
        - ``__ge``: greater than or equal to

        Use of any operator listed here results in a
        :class:`~groupy.api.errors.InvalidOperatorError`.

        :return: a new list with potentially less items than the original
        :rtype: :class:`~groupy.object.listers.FilterList`
        """
        kvops = []
        for k, v in kwargs.items():
            if '__' in k[1:-1]:   # don't use it if at the start or end of k
                k, o = k.rsplit('__', 1)
                try:
                    op = getattr(operator, o)
                except AttributeError:
                    raise errors.InvalidOperatorError("__{}".format(o))
            else:
                op = operator.eq
            kvops.append((k, v, op))
        test = lambda i, k, v, op: hasattr(i, k) and op(getattr(i, k), v)
        criteria = lambda i: all(test(i, k, v, op) for k, v, op in kvops)
        return FilterList(filter(criteria, self))

    @property
    def first(self):
        """The first element in the list.
        """
        try:
            return self[0]
        except IndexError:
            return None

    @property
    def last(self):
        """The last element in the list.
        """
        try:
            return self[-1]
        except IndexError:
            return None


class MessagePager(FilterList):
    """A filterable, extendable page of messages.

    :param group: the group from which to page through messages
    :type group: :class:`~groupy.object.responses.Group`
    :param list messages: the initial page of messages
    :param bool backward: whether the oldest message is at index 0
    """
    def __init__(self, group, messages, backward=False):
        super().__init__(messages)
        self.backward = backward
        self.group = group

    @property
    def oldest(self):
        """Return the oldest message in the list.

        :returns: the oldest message in the list
        :rtype: :class:`~groupy.object.responses.Message`
        """
        return self.first if self.backward else self.last

    @property
    def newest(self):
        """Return the newest message in the list.

        :returns: the newest message in the list
        :rtype: :class:`~groupy.object.responses.Message`
        """
        return self.last if self.backward else self.first

    def prepend(self, messages):
        """Prepend a list of messages to the list.

        :param list messages: the messages to prepend
        """
        for each in messages:
            self.insert(0, each)

    def newer(self):
        """Return the next (newer) page of messages.

        :returns: a newer page of messages
        :rtype: :class:`~groupy.object.listers.MessagePager`
        """
        return self.group.messages(after=self.newest.id)

    def older(self):
        """Return the previous (older) page of messages.

        :returns: an older page of messages
        :rtype: :class:`~groupy.object.listers.MessagePager`
        """
        return self.group.messages(before=self.oldest.id)

    def inewer(self):
        """Add in-place the next (newer) page of messages.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        new = self.newer()
        if not new:
            return False
        if self.backward:
            self.extend(self.newer())
        else:
            self.prepend(self.newer())
        return True

    def iolder(self):
        """Add in-place the previous (older) page of messages.

        :returns: ``True`` if successful, ``False`` otherwise
        :rtype: :obj:`bool`
        """
        old = self.older()
        if not old:
            return False
        if self.backward:
            self.prepend(self.older())
        else:
            self.extend(self.older())
        return True
