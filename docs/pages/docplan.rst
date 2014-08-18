Introduction
============

- GroupMe
	+ It's a group messaging app
		* Group messaging
		* Direct messaging
		* Web, Android, iOS, yada yada yada
- GroupMe API
	+ The good parts
	+ The bad parts
- Groupy
	+ What is it?
	+ What can it do for me?
	+ How easy is it?

Installation
============

- Using pip
- From source

Quickstart
==========

- Whoami?
- The order of things
	+ groups -> messages, members
	+ members -> direct messages
- Fetching stuff
	+ Groups
	+ Members
	+ Messages
- Messaging
	+ Messaging groups
	+ Messaging members
	+ Liking messages
	+ Inspecting messages
- Groups and Members
	+ Adding members to a group
	+ Removing members from a group
- Bots
	+ Creating a bot
	+ Listing bots
	+ Making a bot talk
- Common tasks
	+ Adding a member from one group to another
	+ Restarting a group
	+ Ping everyone in a group
	+ List all members from all groups
	+ Finding the first message in a group

Basic Usage
===========

Listing Things
--------------

Groups, Members, and Bots can be listed directly.

.. code-block:: python

	>>> import groupy
	>>> groups = groupy.Group.list()
	>>> members = groupy.Member.list()
	>>> bots = groupy.Bot.list()

The object lists are returned as a :class:`~groupy.objects.FilterList`. These
behave just like the built-in :class:`list` does, but with some additional
features: :obj:`~groupy.objects.FilterList.first`, and
:obj:`~groupy.objects.FilterList.last`, and

.. code-block:: python

	>>> groups.first == groups[0]
	True
	>>> groups.last == groups[-1]
	True

The most useful feature of a :class:`groupy.objects.FilterList`, however, is its
:func:`~groupy.objects.FilterList.filter` method. It parses whatever keyword
arguments are passed to it and filters the list such that only the items meeting
all criteria are included. The keywords correspond to object properties, but
also indicate how to test the relation to the value of the keyword argument.
Thus a keyword-value pair such as ``name='Bob'`` would keep only those items
with a ``name`` property equal to ``"Bob"``, whereas a pair like ``age__lt=20``
would keep only those items with an ``age`` property *less than* ``20``.

For example, suppose our list of groups has 3 items:

.. code-block:: python

	>>> for g in groups:
	...     print(g.name)
	...
	My Family
	DevTeam #6
	Friday Night Trivia

We want to find only the groups containing "am" in their title. Easy:

.. code-block:: python

	>>> matches = groups.filter(name__contains='am')
	>>> len(matches)
	2
	>>> for m in matches:
	...     print(m.name)
	My Family
	DevTeam #6

Similarly, any :class:`~groupy.objects.FilterList` can be filtered:

.. code-block:: python

	>>> for m in members:
	...     print(m.nickname)
	... 
	Dan the Man
	Manuel
	Fred
	Dan
	>>> for m in members.filter(nickname='Dan'):
	...     print(m.nickname)
	... 
	Dan
	>>> for m in members.filter(nickname__contains='Dan'):
	...     print(m.nickname)
	... 
	Dan the Man
	Dan
	>>> for m in members.filter(nickname__ge='F'):
	...     print(m.nickname)
	... 
	Manuel
	Fred

Groups
------

From a :class:`groupy.objects.Group`, you can list its 
:class:`groupy.objects.Member`s and :class:`groupy.objects.Message`s.

.. code-block:: python

	>>> from groupy import Group
	>>> groups = Group.list()
	>>> group = groups.first
	>>> messages = group.messages()
	>>> members = group.memers()

A group returns all of its members in a single list. However, since there may
be thousands of messages in a group, messages are returned in pages.

.. code-block:: python

	>>> group.message_count
	31229
	>>> len(messages)
	100

To page through the messages, use :func:`groupy.objects.MessagePager.older` and
:func:`groupy.objects.MessagePager.newer`.

.. code-block:: python

	>>> older = messages.older()
	>>> newer = messages.newer()

There are also methods for collecting a newer or older page of messages into one
list: :func:`groupy.objects.MessagePager.iolder` and
:func:`groupy.objects.MessagePager.inewer`. An example of using the former to
retrieve all messages in a group:

.. code-block:: python

	>>> from groupy import Group
	>>> group = Group.list().first
	>>> messages = group.messages()
	>>> while messages.iolder():
	...       pass
	>>> len(messages) == group.message_count
	True

New messages can be posted to a group as well.

.. code-block:: python

	>>> from group import Group
	>>> group = Group.list().first
	>>> group.post('Hello to you')

.. note::

	Posting a message does not affect ``message_count``. However, retrieving any
	page of messages *does* update it.

Messages
--------

- Likes

Members
-------

Bots
----

Advanced Usage
==============

- Working with lists
	+ Filter lists
	+ Messsage pagers
- Creating attachments
	+ Images
	+ Locations
	+ Emoji
- When it just doesn't work out...
	+ Leaving a group
	+ Disbanding (destroying) a group you own
	+ Destroying a bot
- The SMS mode
	+ Enabling and you
	+ Disabling
