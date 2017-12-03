import urllib


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
