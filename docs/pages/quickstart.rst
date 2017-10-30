==========
Quickstart
==========

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

Listing groups
--------------

.. code-block:: python

    >>> page_one = client.groups.list()
    >>> page_two = client.groups.list(page=2)
    >>> probably_all_groups = client.groups.list(per_page=100)
    >>> all_groups = list(client.groups.list().autopage())


Listing chats
-------------

.. code-block:: python

    >>> chats = client.chats.list()


Listing bots
------------

.. code-block:: python

    >>> bots = client.bots.list()


Getting your own user information
---------------------------------

.. code-block:: python

    >>> cached_user_data = client.user.me
    >>> fresh_user_data = client.user.get_me()


Working with resources
======================

In general, if a field is present in an API response, you can access it as an attribute of the resource. For example:

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

    >>> new_group = client.groups.create(name='Yay, I have my own group')

Listing messages from a group
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> messages = group.messages.list()

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
=====

Listing messages
----------------

.. code-block:: python

    >>> messages = chat.messages.list()

.. note:: See "Listing messages" for details.


Messages
========

Creating a message (in a group)
-------------------------------

.. code-block:: python

    >>> message = group_or_chat.post(text='hi')

Liking/Unliking a message
-------------------------

.. code-block:: python

    >>> message.like()
    >>> message.unlike()

Listing messages
----------------

.. code-block:: python

    >>> messages = chat_or_group.messages.list()
    >>> oldest_message_in_page = messages[-1]
    >>> page_two = chat_or_group.messages.list_before(oldest_message_in_page.id)
    >>> all_messages = list(chat_or_group.messages.list().autopage())


Members
=======

Blocking/Unblocking a member
----------------------------

.. code-block:: python

    >>> block = member.block()
    >>> member.unblock()

Removing members from groups
----------------------------

.. note:: Remember, members are specific to the group from which they were obtained.

.. code-block:: python

    >>> member.remove()
