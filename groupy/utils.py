import urllib
import operator
from functools import partial

from groupy import exceptions


def urljoin(base, path=None):
    """Join a base url with a relative path."""
    # /foo/bar + baz makes /foo/bar/baz instead of /foo/baz
    if path is None:
        url = base
    else:
        if not base.endswith('/'):
            base += '/'
        url = urllib.parse.urljoin(base, str(path))
    return url


def parse_share_url(share_url):
    """Return the group_id and share_token in a group's share url.

    :param str share_url: the share url of a group
    """
    *__, group_id, share_token = share_url.rstrip('/').split('/')
    return group_id, share_token


class AttrTest:
    def __init__(self, key, value):
        self._key = key
        if '__' in key[1:-1]:
            attr, op_name = key.rsplit('__', 1)
            op = getattr(operator, op_name)
        else:
            attr = key
            op = operator.eq
        self.attr = attr
        self.op = op
        self.value = value

    def __repr__(self):
        return '{0._key}={0.value}'.format(self)

    def __call__(self, obj):
        try:
            attr = getattr(obj, self.attr)
        except AttributeError:
            return False
        else:
            return self.op(attr, self.value)


class Filter:
    def __init__(self, tests):
        self.tests = tests

    def __call__(self, objects):
        yield from filter(self.passes, objects)

    def find(self, objects):
        matches = list(self.__call__(objects))
        if not matches:
            raise exceptions.NoMatchesError(objects, self.tests)
        elif len(matches) > 1:
            raise exceptions.MultipleMatchesError(objects, self.tests,
                                                  matches=matches)
        return matches[0]

    def passes(self, obj):
        return all(test(obj) for test in self.tests)


def make_filter(**tests):
    tests = [AttrTest(k, v) for k, v in tests.items()]
    return Filter(tests)
