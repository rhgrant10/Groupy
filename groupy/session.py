import logging

import requests

from . import exceptions


logger = logging.getLogger(__name__)


class Session(requests.Session):
    """An HTTP session for making API requests.

    This session sets the content type to JSON and injects the API token.
    """

    def __init__(self, token):
        super().__init__()
        self.headers = {
            'content-type': 'application/json',
            'x-access-token': token,
        }

    def request(self, *args, **kwargs):
        # ensure we reraise exceptions as our own
        try:
            response = super().request(*args, **kwargs)
            response.raise_for_status()
            return Response(response)
        except requests.HTTPError as e:
            logger.exception('received a bad response')
            raise exceptions.BadResponse(response) from e
        except requests.RequestException as e:
            logger.exception('could not receive a response')
            raise exceptions.NoResponse(e.request) from e


class Response:
    def __init__(self, response):
        self._resp = response

    # pretend we're a requests.Response
    def __getattr__(self, attr):
        return getattr(self._resp, attr)

    @property
    def data(self):
        try:
            return self.json()['response']
        except ValueError as e:
            raise exceptions.InvalidJsonError(self._resp) from e
        except KeyError as e:
            try:
                return self.json()['payload']
            except KeyError:
                raise exceptions.MissingResponseError(self._resp) from e

    @property
    def errors(self):
        try:
            return self.json()['meta']['errors']
        except ValueError as e:
            raise exceptions.InvalidJsonError(self._resp) from e
        except KeyError as e:
            raise exceptions.MissingMetaError(self._resp) from e
