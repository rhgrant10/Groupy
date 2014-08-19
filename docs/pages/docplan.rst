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

The most useful feature of a :class:`groupy.objects.FilterList`, however, is
its :func:`~groupy.objects.FilterList.filter` method. It parses whatever
keyword arguments are passed to it and filters the list such that only the
items meeting all criteria are included. The keywords correspond to object
properties, but also indicate how to test the relation to the value of the
keyword argument. Thus a keyword-value pair such as ``name='Bob'`` would keep
only those items with a ``name`` property equal to ``"Bob"``, whereas a pair
like ``age__lt=20`` keeps only those items with an ``age`` property *less than*
``20``.

Some simple examples: 

.. code-block:: python

	>>> from groupy import Group
	>>> groups = Group.list()
	>>> for g in groups:
	...     print(g.name)
	...
	My Family
	DevTeam #6
	Friday Night Trivia
	>>> for g in groups.filter(name__contains='am'):
	...     print(g.name)
	My Family
	DevTeam #6
	>>> 
	>>> members = groups.first.members()
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

.. todo::

	Add section about modifying a group.

From a :class:`groupy.objects.Group`, you can list its 
:class:`groupy.objects.Member`s and :class:`groupy.objects.Message`s.

.. code-block:: python

	>>> from groupy import Group
	>>> groups = Group.list()
	>>> group = groups.first
	>>> messages = group.messages()
	>>> members = group.memers()

A group returns all of its members in a single list. So determining the number
of members in a group is familiar.

.. code-block:: python

	>>> len(members)
	5

Messages, however, are a different matter. Since there may be thousands of
messages in a group, messages are returned in pages.

.. code-block:: python

	>>> len(messages)
	100
	
The total number of messages in the group is in ``message_count``.

.. code-block::python

	>>> group.message_count
	3014

To page through the messages, use :func:`groupy.objects.MessagePager.older` and
:func:`groupy.objects.MessagePager.newer`.

.. code-block:: python

	>>> older = messages.older()
	>>> newer = messages.newer()

There are also methods for collecting a newer or older page of messages into
one list: :func:`groupy.objects.MessagePager.iolder` and
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
	>>> print(group.messages().newest.text)
	'Hello to you'

.. note::

	Posting a message does not affect ``message_count``. However, retrieving
	any page of messages *does* update it.

Messages
--------

Unlike :class:`groupy.objects.Group`s, :class:`groupy.objects.Member`s, and
:class:`groupy.objects.Bot`s, :class:`groupy.objects.Message`s **cannot** be
listed directly. Instead, :class:`groupy.objects.Message`s are listed either
from :class:`groupy.objects.Group` or :class:`groupy.objects.Member` instances.

To list the messages from a group, first obtain the group and then list its
messages.

.. code-block:: python

	>>> from groupy import Group
	>>> group = Group.list().first
	>>> messages = group.messages()

To list the direct messages with another member, obtain the member and then
list the messages.

.. code-block:: python

	>>> from groupy import Member
	>>> member = Member.list().first
	>>> messages = member.messages()

Messages have several properties. Let's look at a few of them. Messages have a
timestamp indicating when the message was created.

.. code-block:: python

	>>> message = messages.newest
	>>> message.created_at
	2014-4-29 12:19:05

As with other API objects, timestamp data is returned as 
:class:`datetime.datetime` instances.

Messages also contain information about the member who posted it.

	>>> message.user_id
	'0123456789'
	>>> message.name
	'Kevin'
	>>> message.avatar_url
	'http://i.groupme.com/a01b23c45d56e78f90a01b12c3456789'

Of course, messages have text and attachments. A message may or may not have
text or attachments, but every message must have one or the other.

	>>> message.text
	'Hello'
	>>> message.attachments
	[Image(url='http://i.groupme.com/a01b23c45d56e78f90a01b12c3456789')]

Although the majority of messages will have just one attachment, there is no
limit on the number of attachments. In fact, despite most clients being
incapable of displaying them, the API doesn't even limit the number of each
kind of attachment. For example, a single message might have two images, three
locations, and one emoji.

There are multiple types of messages. System messages are messages that are not
sent by a member, but generated by member actions. Many things generate system
messages, including member changes, group updates (name, avatar, etc.), member
changes (nickname, avatar, etc.), and changing the topic.

Additionally there are group messages and direct messages. Group messages are
messages in a group, whereas direct messages are messages between two members.

Each message has a few properties that can be used to differentiate the types.

	>>> message.group_id
	'1234567890'
	>>> message.recipient_id
	None
	>>> message.system
	False

In the above example, we can see that ``message.system`` is ``False``, which
indicates that the message was sent by a member, not the system. We can also
see that although the message has a ``message.group_id``, it does *not* have a
``message.recipient_id``, which means it is a group message. Had it been a
system message, ``message.system`` would have been ``True``. Had it been a
direct message, ``message.group_id`` would have been ``None`` and
``message.recipient_id`` would contain a valid user ID.

Lastly, each message contains a list of user IDs to indicate which members have
"liked" it.

	>>> message.favorited_by
	['2345678901', '3456789012']

Because often more information about the member is desired, a list of actual
:class:`groupy.objects.Member` instances can be retrieved using the
:func:`groupy.objects.Message.likes` method.

.. code-block:: python

	>>> message.likes()
	[Rob, Jennifer, Vlad]

Messages can also be liked and unliked.

.. code-block:: python

	>>> message.like()
	True
	>>> message.unlike()
	True

.. note::

	Currently, the message instance itself does **not** update its own
	attributes. You must re-fetch the message.


Members
-------

:class:`groupy.objects.Member` instances represent other GroupMe users. Finding
members can be accomplished in one of three ways. First, all the members you've
seen thus far can be listed directly.

.. code-block:: python

	>>> from groupy import Member
	>>> members = Member.list()

.. note::

	The name (or nickname) of each member listed from
	:func:`group.objects.Member.list` is the most frequent of the names that
	the member uses among the groups of which you are both members.

Secondly, members may be listed from a group. Of course, this lists only the
members of one group.

.. code-block:: python

	>>> from groupy import Group
	>>> group = Group.list().first
	>>> members = group.members()

Lastly, members may be listed from a message. This lists the members who have
"liked" the message.

.. code-block:: python

	>>> messages = group.messages()
	>>> message = message.newest
	>>> members = message.likes()

Each member has a user ID, a nickname, and a URL indicating their avatar image
that are specific to the group from which the member was listed.

.. code-block:: python

	>>> member = members.first
	>>> member.user_id
	'0123456789'
	>>> member.nickname
	'Bill'
	>>> member.avatar_url
	'http://i.groupme.com/a01b23c45d56e78f90a01b12c3456789'

Members have one more property of interest: ``muted``. This indicates whether
the member has that group muted.

.. code-block:: python

	>>> member1, member2 = members[:2]
	>>> member1.muted
	False
	>>> member2.muted
	True

Messaging a member and retrieving the messages between you and the member is
done in the same way as when messaging a group.

.. code-block:: python

	>>> member.post("Hello")
	>>> member.messages().newest.text
	'Hello'

Bots
----

- Can be listed
- Can be created
- Can be modified
- Can post messages
- Can be deleted

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
