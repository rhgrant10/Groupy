import urllib
import operator
from datetime import datetime, timezone, timedelta

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


def get_rfc3339(when):
    """Return an RFC 3339 timestamp.

    :param datetime.datetime when: a datetime in UTC
    :return: RFC 3339 timestamp
    :rtype: str
    """
    microseconds = format(when.microsecond, '04d')[:4]
    rfc3339 = '%Y-%m-%dT%H:%M:%S.{}Z'
    return when.strftime(rfc3339.format(microseconds))


def get_datetime(timestamp):
    # for very strange/wrong dates: https://stackoverflow.com/a/36180569/8207
    epoch = datetime.fromtimestamp(0, timezone.utc)
    return epoch + timedelta(seconds=timestamp)


class AttrTest:
    """An attribute value test.

    :param str key: attribute key
    :param value: value against which to compare
    """

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
    """A callable filter composed of one or more tests.

    :param tests: tests to perform
    """
    def __init__(self, tests):
        self.tests = tests

    def __call__(self, objects):
        yield from filter(self.passes, objects)

    def find(self, objects):
        """Find exactly one match in the list of objects.

        :param objects: objects to filter
        :type objects: :class:`list`
        :return: the one matching object
        :raises groupy.exceptions.NoMatchesError: if no objects match
        :raises groupy.exceptions.MultipleMatchesError: if multiple objects match
        """
        matches = list(self.__call__(objects))
        if not matches:
            raise exceptions.NoMatchesError(objects, self.tests)
        elif len(matches) > 1:
            raise exceptions.MultipleMatchesError(objects, self.tests,
                                                  matches=matches)
        return matches[0]

    def passes(self, obj):
        """Test one object.

        :param obj: the object to test
        :return: ``True`` if the object passes all tests
        :rtype: bool
        """
        return all(test(obj) for test in self.tests)


def make_filter(**tests):
    """Create a filter from keyword arguments."""
    tests = [AttrTest(k, v) for k, v in tests.items()]
    return Filter(tests)
