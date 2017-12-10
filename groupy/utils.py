import urllib
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


class Filter:
    def __init__(self, **tests):
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
        try:
            return all(getattr(obj, name) == value for name, value in self.tests.items())
        except AttributeError:
            return False


def make_filter(**tests):
    return Filter(**tests)
