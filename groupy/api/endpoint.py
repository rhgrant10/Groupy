"""
.. module:: endpoint
    :platform: Unix, Windows
    :synopsis: A module containing the various API endpoints

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

This module contains classes that represent the many endpoints in the GroupMe
API.

"""
import time
import json
from io import BytesIO

import requests
from PIL import Image as PImage

from .. import config
from . import errors


class Endpoint:
    '''An API endpoint capable of building a url and extracting data from the
    response.

    This class serves as the base class for all of the API endpoints.
    '''
    url = config.API_URL

    @classmethod
    def build_url(cls, path=None, *args):
        """Build and return a url extended by *path* and filled in with *args*.

        :param str path: a suffix for the final URL. If *args* are present,
            this should be a python format string pertaining to the given
            *args*.
        :param list args: a list of arguments for the format string *path*.
        :returns: a complete URL
        :rtype: str
        """
        try:
            url = '/'.join([cls.url, path.format(*args)])
        except AttributeError:
            if path is None:
                url = cls.url
            else:
                url = '/'.join([cls.url, str(path)])
        except TypeError:
            # This can only occur when cls.url is not a string! Give a better
            # error message instead of letting this crap happen.
            url = cls.url
        return '?'.join([url, 'token={}'.format(config.API_KEY)])

    @classmethod
    def response(cls, r):
        """Extract the data from the API response *r*.

        This method essentially strips the actual response of the envelope
        while raising an :class:`~errors.ApiError` if it contains one or more
        errors.

        :param r: the HTTP response from an API call
        :type r: :class:`requests.Response`
        :returns: API response data
        :rtype: json
        """
        try:
            data = r.json()
        except ValueError:
            raise errors.ApiError(r)
        if data['meta'].get("errors"):
            raise errors.ApiError(data['meta'])
        return data["response"]

    @staticmethod
    def clamp(value, lower, upper):
        """Utility method for clamping a *value* between a *lower* and an
        *upper* value.

        :param value: the value to clamp
        :param lower: the "smallest" possible value
        :param upper: the "largest" possible value
        :returns: *value* such that ``lower <= value <= upper``
        """
        return max(lower, min(value, upper))


class Groups(Endpoint):
    """Endpoint for the groups API.

    Groups can be listed, loaded, created, updated, and destroyed.
    """
    url = '/'.join([Endpoint.url, 'groups'])

    @classmethod
    def show(cls, group_id):
        """Return a specific group by its *group_id*.

        :param str group_id: the ID of the group to show.
        :returns: the group with the given *group_id*
        :rtype: :class:`dict`
        """
        r = requests.get(cls.build_url(group_id))
        return cls.response(r)

    @classmethod
    def index(cls, page=1, per_page=500, former=False):
        """Return a list of groups.

        :param int page: the page of groups to return
        :param int per_page: the number of groups in the page
        :param bool former: whether to list former groups instead
        :returns: a list of groups
        :rtype: :class:`list`
        """
        per_page = cls.clamp(per_page, 1, 500)
        r = requests.get(
            cls.build_url('former') if former else cls.build_url(),
            params={
                'page': page,
                'per_page': per_page
            }
        )
        return cls.response(r)

    @classmethod
    def create(cls, name, description=None, image_url=None, share=True):
        """Create a new group.

        :param str name: the name of the new group
        :param str description: the description of the new group
        :param str image_url: the group avatar image as a GroupMe image URL
        :param bool share: whether to generate a join link for the group
        :returns: the new group
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url(),
            params={
                'name': name,
                'description': description,
                'image_url': image_url,
                'share': share
            }
        )
        return cls.response(r)

    @classmethod
    def update(cls, group_id,
               name=None, description=None, share=None, image_url=None):
        """Update the information for a group.

        :param str group_id: the ID of the group to update
        :param str name: the new name of the group
        :param str description: the new description of the group
        :param bool share: whether to generate a join link for the group
        :param str image_url: the GroupMe image URL for the new group avatar.
        :returns: the modified group
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url('{}/update', group_id),
            params={
                'name': name,
                'description': description,
                'image_url': image_url,
                'share': share
            }
        )
        return cls.response(r)

    @classmethod
    def destroy(cls, group_id):
        """Destroy (or leave) a group.

        .. note::

            If you are not the owner of a group, you cannot destroy it.

        :param str group_id: the ID of the group to destroy/leave
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url('{}/destroy', group_id)
        )
        return cls.response(r)


class Members(Endpoint):
    """Endpoint for the members API.

    Members can be added and removed from a group, and the results of adding
    members can be obtained.
    """
    url = '/'.join([Endpoint.url, 'groups'])

    @classmethod
    def add(cls, group_id, *members):
        """Add one or more members to a group.

        :param str group_id: the ID of the group to which the members should
            be added
        :param list members: the members to add.
        :returns: the results ID for this request
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url('{}/members/add', group_id),
            data=json.dumps({'members': members}),
            headers={'content-type': 'application/json'})
        return cls.response(r)

    @classmethod
    def results(cls, group_id, result_id):
        """Check the result of adding one or more members.

        :param str group_id: the ID of the group to which the add call was made
        :param str result_id: the GUID returned by the add call
        :returns: the successfully added members
        :rtype: :class:`list`
        """
        r = requests.get(
            cls.build_url('{}/members/results/{}', group_id, result_id)
        )
        return cls.response(r)

    @classmethod
    def remove(cls, group_id, member_id):
        """Remove a member from a group.

        :param str group_id: the ID of the group from which the member should
            be removed
        :param str member_id: the ID of the member to remove
        """
        r = requests.post(
            cls.build_url('{}/members/{}/remove', group_id, member_id)
        )
        return cls.response(r)


class Messages(Endpoint):
    """Endpoint for the messages API.

    Messages can be listed and created.
    """
    url = '/'.join([Endpoint.url, 'groups'])

    @classmethod
    def index(cls, group_id,
              before_id=None, since_id=None, after_id=None, limit=100):
        """List the messages from a group.

        Listing messages gives the most recent 100 by default. Additional
        messages can be obtained by specifying a reference message, thereby
        facilitating paging through messages.

        Use ``before_id`` and ``after_id`` to "page" through messages.
        ``since_id`` is odd in that it returns the *most recent* messages
        since the reference message, which means there may be messages missing
        between the reference message and the oldest message in the returned
        list of messages.

        .. note::

            Only one of ``before_id``, ``after_id``, or ``since_id`` can be
            specified in a single call.

        :param str group_id: the ID of the group from which to list messages
        :param str before_id: a reference message ID; specify this to list
            messages just prior to it
        :param str since_id: a reference message ID; specify this to list
            the *most recent* messages after it
            (**not** the messages right after the reference message)
        :param str after_id: a reference message ID; specifying this will
            return the messages just after the reference message
        :param int limit: a limit on the number of messages returned (between
            1 and 100 inclusive)
        :returns: a :class:`dict` containing ``count`` and ``messages``
        :rtype: :class:`dict`
        :raises ValueError: if more than one of ``before_id``, ``after_id`` or
            ``since_id`` are specified
        """
        # Check arguments.
        not_None_args = []
        for arg in (before_id, since_id, after_id):
            if arg is not None:
                not_None_args.append(arg)
        if len(not_None_args) > 1:
            raise ValueError("Only one of 'after_id', 'since_id', and "
                             "'before_id' can be specified in a single call")

        limit = cls.clamp(limit, 1, 100)
        r = requests.get(
            cls.build_url('{}/messages', group_id),
            params={
                'after_id': after_id,
                'limit': limit,
                'before_id': before_id,
                'since_id': since_id
            }
        )
        return cls.response(r)

    @classmethod
    def create(cls, group_id, text, *attachments):
        """Create a new message in a group.

        All messages must have either text or one attachment. Note that while
        the API provides for an unlimited number of attachments, most clients
        can only handle one of each attachment type (location, image, split, or
        emoji).

        :param str group_id: the ID of the group in which to create the message
        :param str text: the text of the message
        :param list attachments: a list of attachments to include
        :returns: the created message
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url('{}/messages', group_id),
            data=json.dumps({
                'message': {
                    'source_guid': str(time.time()),
                    'text': text,
                    'attachments': attachments
                }
            }),
            headers={'content-type': 'application/json'}
        )
        return cls.response(r)


class DirectMessages(Endpoint):
    """Endpoint for the direct message API.
    """
    url = '/'.join([Endpoint.url, 'direct_messages'])

    @classmethod
    def index(cls, other_user_id, before_id=None, since_id=None, after_id=None):
        """List the direct messages with another user.

        :param str other_user_id: the ID of the other party
        :param str before_id: a reference message ID; specify this to list
            messages prior to it
        :returns: a list of direct messages
        :rtype: :class:`list`
        """
        r = requests.get(
            cls.build_url(),
            params={
                'other_user_id': other_user_id,
                'before_id': before_id,
                'since_id': since_id,
                'after_id': after_id
            }
        )
        return cls.response(r)

    @classmethod
    def create(cls, recipient_id, text, *attachments):
        """Create a direct message to a recipient user.

        :param str recipient_id: the ID of the recipient
        :param str text: the message text
        :param list attachments: a list of attachments to include
        :returns: the created direct message
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url(),
            data=json.dumps({
                'direct_message': {
                    'source_guid': str(time.time()),
                    'recipient_id': recipient_id,
                    'text': text,
                    'attachments': attachments
                }
            }),
            headers={'content-type': 'application/json'}
        )
        return cls.response(r)


class Likes(Endpoint):
    """Endpoint for the likes API.

    Likes can be created or destroyed.

    .. note::

        The ``conversation_id`` is poorly documented. For messages in a group,
        it corresponds to the ``group_id`` (or ``id`` since they seem to always
        be identical). For direct messages, it corresponds to the ``user_id``
        of both conversation participants sorted lexicographically and
        concatenated with a plus sign ("+").

    """
    url = '/'.join([Endpoint.url, 'messages'])

    @classmethod
    def create(cls, conversation_id, message_id):
        """Like a message.

        :param str conversation_id: the ID of the group or recipient
        :param str message_id: the ID of the message
        """
        r = requests.post(
            cls.build_url('{}/{}/like', conversation_id, message_id)
        )
        return cls.response(r)

    @classmethod
    def destroy(cls, conversation_id, message_id):
        """Unlike a message.

        :param str conversation_id: the ID of the group or recipient
        :param str message_id: the ID of the message
        """
        r = requests.post(
            cls.build_url('{}/{}/unlike', conversation_id, message_id)
        )
        return cls.response(r)


class Bots(Endpoint):
    """Endpoint for the bots API.

    Bots can be listed, created, updated, and destroyed. Bots can also post
    messages to groups.
    """
    url = '/'.join([Endpoint.url, 'bots'])

    @classmethod
    def index(cls):
        """List bots.

        :returns: a list of bots
        :rtype: :class:`list`
        """
        r = requests.get(
            cls.build_url()
        )
        return cls.response(r)

    @classmethod
    def create(cls, name, group_id, avatar_url=None, callback_url=None):
        """Create a new bot.

        :param str name: the name of the bot
        :param str group_id: the ID of the group to which the bot will belong
        :param str avatar_url: the GroupMe image URL for the bot's avatar
        :param str callback_url: the callback URL for the bot
        :returns: the new bot
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url(),
            data=json.dumps({
                "bot": {
                    'name': name,
                    'group_id': group_id,
                    'avatar_url': avatar_url,
                    'callback_url': callback_url
                }
            }),
            headers={'content-type': 'application/json'}
        )
        return cls.response(r)

    @classmethod
    def post(cls, bot_id, text, picture_url=None):
        """Post a message to a group as a bot.

        :param str bot_id: the ID of the bot
        :param str text: the message text
        :param str picture_url: the GroupMe image URL for a picture
        :returns: the created message
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url('post'),
            data=json.dumps({
                'bot_id': bot_id,
                'text': text,
                'picture_url': picture_url
            }),
            headers={'content-type': 'application/json'}
        )
        return cls.response(r)

    @classmethod
    def destroy(cls, bot_id):
        """Destroy a bot.

        :param str bot_id: the ID of the bot to destroy
        """
        r = requests.post(
            cls.build_url('destroy'),
            params={'bot_id': bot_id}
        )
        return cls.response(r)


class Users(Endpoint):
    """Endpoint for the users API.
    """
    url = '/'.join([Endpoint.url, 'users'])

    @classmethod
    def me(cls):
        """Get the user's information.

        :returns: the user's information
        :rtype: :class:`dict`
        """
        r = requests.get(
            cls.build_url('me')
        )
        return cls.response(r)


class Sms(Endpoint):
    """Endpoint for the SMS API.

    SMS mode can be enabled or disabled.
    """
    url = '/'.join([Endpoint.url, 'users', 'sms_mode'])

    @classmethod
    def create(cls, duration=4, registration_id=None):
        """Enable SMS mode.

        :param int duration: duration of SMS mode in hours (max of 48)
        :param str registration_id: the push registration_id or token to
            suppress (if omitted, SMS and push notifications will both
            be enabled)
        """
        duration = cls.clamp(duration, 1, 48)
        r = requests.post(
            cls.build_url(),
            params={
                'duration': duration,
                'registration_id': registration_id
            }
        )
        return cls.response(r)

    @classmethod
    def delete(cls):
        """Disable SMS mode.
        """
        r = requests.post(
            cls.build_url('delete')
        )
        return cls.response(r)


class Images(Endpoint):
    """Endpoint for the image service API.

    GroupMe images are created through an upload service that returns a URL at
    which it can be accessed.
    """
    url = '/'.join([config.IMAGE_API_URL, 'pictures'])

    @classmethod
    def response(cls, r):
        """Extract the data from the image service API response *r*.

        This method basically returns the inner "payload."

        :param r: the HTTP response from an API call
        :type r: :class:`requests.Response`
        :returns: API response data
        :rtype: json
        """
        try:
            data = r.json()
        except ValueError:
            raise errors.ApiError(r)
        return data['payload']

    @classmethod
    def create(cls, image):
        """Submit a new image.

        :param image: object with a file-like interface and containing an
            image
        :type image: :obj:`file`
        :returns: the URL at which the image can be accessed
        :rtype: :class:`dict`
        """
        r = requests.post(
            cls.build_url(),
            files={'file': image}
        )
        return cls.response(r)

    @classmethod
    def download(cls, url):
        r = requests.get(url)
        image = BytesIO(r.content)
        try:
            return PImage.open(image)
        except OSError:
            return None
