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
