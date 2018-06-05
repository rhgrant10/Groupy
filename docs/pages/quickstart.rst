===============
Getting Started
===============

First, make sure you have:

- **Groupy** installed
- your API key

See the :doc:`installation` page for help if needed.


The Client
==========

Creating a client
-----------------

Assuming your API token is stored in ``token``:

.. code-block:: python

    >>> from groupy.client import Client
    >>> client = Client.from_token(token)

Clients are capable of listing groups, chats, and bots. It can also provide your user
information.

Listing groups
--------------

Groups are listed in pages. You can specify which page and how many groups per page
using the ``page`` and ``per_page`` parameters. ``per_page`` defaults to 10.

.. code-block:: python

    >>> client.groups.list()
    <groupy.pagers.GroupList at 0x7fcd9f7174e0>
    >>> client.groups.list(page=2, per_page=30)
    <groupy.pagers.GroupList at 0x7fa02c23db70>

The :class:`~groupy.pagers.GroupList` returned can be iterated to obtain the groups
in that page.

.. code-block:: python

    >>> for group in client.groups.list():
    ...     print(group.name)

Since paging can be a pain, the :class:`~groupy.pagers.GroupList` also possesses an
:func:`~groupy.pagers.Pager.autopage` method that can be used to obtain all groups
by automatically handling paging:

.. code-block:: python

    >>> groups = client.groups.list()
    >>> for group in groups.autopage():
    ...     print(group.name)

However, the easiest way to list all groups, is:

.. code-block:: python

    >>> for group in client.groups.list_all():
    ...     print(group.name)

.. note::

    The ordering of groups is determined by most recent activity, so the group with
    the youngest message will be listed first. For this reason, autopaging is highly
    recommended when the goal is to list all groups.


Omitting fields
^^^^^^^^^^^^^^^

Sometimes, particularly when a group contains hundreds of members, the response is
"too large" and contains an incomplete response. In that case, an
:class:`~groupy.exceptions.InvalidJsonError` is raised.

To avoid this, use the ``omit`` parameter to specify fields to omit.

.. code-block:: python

    >>> groups = client.groups.list(omit="memberships")

.. note::

    Multiple fields must be formatted in a CSV (e.g. "memberships,description").
    At the time of this writing, however, the API only supports omission of
    "memberships."

To refresh a group with fresh data from the server, thus replenishing any missing
fields, use :func:`refresh_from_server`:

.. code-block:: python

    >>> group.refresh_from_server()


Listing chats
-------------

Listing chats is exactly list listing groups, except that you cannot choose to
omit fields.

.. code-block:: python

    >>> for chat in client.chats.list_all():
    ...     print(chat.other_user['name'])


Listing bots
------------

Bots are listed all in one go. That is, the list of bots you own is not paginated.

.. code-block:: python

    >>> for bot in client.bots.list():
    ...     print(bot.name)


Your own user information
-------------------------

At any time, you can easily access information about your GroupMe user account
as a simple dictionary:

.. code-block:: python

    >>> fresh_user_data = client.user.get_me()

Since user information does not typically change during the lifetime
of a single client instance, the user information is cached the first time it
is fetched. You can access the cached user information as a read-only property:

.. code-block:: python

    >>> cached_user_data = client.user.me


Resources
=========

In general, if a field is present in an API response, you can access it
as an attribute of the resource. For example:

.. code-block:: python

    >>> group.name
    'My cool group'
    >>> member.id
    '123456789'

Some fields are converted to more useful objects for you:

    >>> message.created_at
    datetime.datetime(2015, 2, 8, 2, 8, 40)


Groups
------

Creating new groups
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> new_group = client.groups.create(name='My group')

Listing messages from a group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> message_page = group.messages.list()
    >>> for message in group.messages.list_all():
    ...     print(message.text)
    ...
    >>> message_page = group.messages.list_after(message_id=message)

.. note:: See "Listing messages" for details.


Accessing members of a group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> members = group.members


Viewing the leaderboard
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> daily_best = group.leaderboard.list_day()
    >>> weekly_best = group.leaderboard.list_week()
    >>> my_best = group.leaderboard.list_for_me()


Viewing the gallery
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> messages = group.gallery.list()

Destroying a group
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> if group.destroy():
    ...     print('Bye bye!')
    ... else:
    ...     print('Something went wrong...')


Chats
-----

A chat represents a conversation between you and another user.

Listing messages
^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> messages = chat.messages.list()

.. note:: See the section on messages below for details.


Members
-------

Blocking/Unblocking a member
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> block = member.block()
    >>> member.unblock()

Removing members from groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Remember, members are specific to the group from which they are
    obtained.

.. code-block:: python

    >>> member.remove()


Messages
--------

Creating a message (in a group)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> message = group_or_chat.post(text='hi')

Liking/Unliking a message
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> message.like()
    >>> message.unlike()

Listing messages
^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> messages = chat_or_group.messages.list()
    >>> oldest_message_in_page = messages[-1]
    >>> page_two = chat_or_group.messages.list_before(oldest_message_in_page.id)
    >>> all_messages = list(chat_or_group.messages.list().autopage())


Attachments
-----------

Currently, **Groupy** supports the following types of attachments:

- :class:`~groupy.api.attachments.Location` - for locations
- :class:`~groupy.api.attachments.Image` - for images
- :class:`~groupy.api.attachments.Mentions` - for "@" mentions
- :class:`~groupy.api.attachments.Emoji` - for emoticons
- :class:`~groupy.api.attachments.Split` - for splitting bills *(deprecated)*

For all other types of attachments (such as those introduced in the future)
there exists a generic :class:`~groupy.api.attachments.Attachment` class.

The following sections cover the various types of attachments and how to create
them. Assume we have already imported the attachments module:

    >>> from groupy import attachments

Locations
^^^^^^^^^

:class:`~groupy.api.attachments.Location` attachments are the simplest of all
attachment types. Each includes a ``name``, a latitude ``lat``, and a longitude
``lng``. Some location attachments also contain a ``foursqure_venue_id``.

.. code-block:: python

    >>> location = attachments.Location(name='Camelot', lat=42, lng=11.2)

Images
^^^^^^

:class:`~groupy.api.attachments.Image` attachments are unique in that they do
not actually contain the image data. Instead, they specify the URL from which
you can obtain the actual image. To create a new image from a local file object,

.. code-block:: python

    >>> with open('some-image', 'rb') as f:
    >>>     image = client.images.from_file(f)

To fetch the actual image bytes of an image attachment, use the ``client``:

.. code-block:: python

    >>> image_data = client.images.download(image)


Mentions
^^^^^^^^

:class:`~groupy.api.attachments.Mentions` are an undocumented type of
attachment.  However, they are simple to understand. Mentions capture the
details necessary to highlight "@" mentions of members in groups. They
contain a list of ``loci`` and an equal-sized list of ``user_ids``.

Assuming Bob's user ID is 1234, the mention of Bob in "Hi @Bob!" would be:

.. code-block:: python

    >>> mention = attachments.Mentions(loci=[(3, 4)],
    ...                                user_ids=['1234'])

Each element in ``loci`` has two integers, the first of which indicates the
starting index of the mentioning text, while second indicates its length.
The strings in ``user_ids`` correspond *by index* to the elements in ``loci``.
You can use the ``loci`` to extract the mentioning portion of the text, as
well as obtain the mentioned member via ``user_ids``.

An example with mutiple mentions probably illustrates this better. If Bill
(user ID 2345) and Zoe Childs (user ID 6789) are mentioned in "@Bill hey I
saw you with @Zoe Childs at the park!'"

.. code-block:: python

    >>> mentions = attachments.Mentions(loci=[[0, 5], [25, 11]],
    ...                                 user_ids=['2345', '6789'])



Emojis
^^^^^^

:class:`~groupy.api.attachments.Emojis` are also an undocumented type of
attachment, yet frequently appear in messages. Emoji attachments have a
``placeholder`` and a ``charmap``. The ``placeholder`` is a high-point or
unicode character designed to mark the location of the emoji in the text of
the message. The ``charmap`` serves as some sort of translation or lookup
tool for obtaining the actual emoji.

Splits
^^^^^^

.. note::

    This type of attachment is depreciated. They were part of GroupMe's bill
    splitting feature that seems to no longer be implemented in their clients.
    **Groupy**, however, still supports them due to their presence in older
    messages.
