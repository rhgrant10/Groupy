===========
Basic Usage
===========

This page gives an overview of all but the most advanced features of **Groupy**.

First, you'll want to make sure that 

- **Groupy** is *installed*
- **Groupy** can *find your API key*

See the :doc:`installation` page for instructions. Now that that's out of the
way, let's get started!



Listing Things
==============

Groups, Members, and Bots can be listed directly.

.. code-block:: python

    >>> import groupy
    >>> groups = groupy.Group.list()
    >>> members = groupy.Member.list()
    >>> bots = groupy.Bot.list()

The object lists are returned as a :class:`~groupy.objects.FilterList`. These
behave just like the built-in :class:`list` does, but with some additional
features: :obj:`~groupy.objects.FilterList.first` and
:obj:`~groupy.objects.FilterList.last`.

.. code-block:: python

    >>> groups.first == groups[0]
    True
    >>> groups.last == groups[-1]
    True

The most useful feature of a :class:`~groupy.objects.FilterList`, however, is
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
======

.. todo::

    Add section about modifying a group.

From a :class:`~groupy.objects.Group`, you can list its 
:class:`~groupy.objects.Member`\ s and :class:`~groupy.objects.Message`\ s.

.. code-block:: python

    >>> from groupy import Group
    >>> groups = Group.list()
    >>> group = groups.first
    >>> messages = group.messages()
    >>> members = group.memers()

A group returns all of its members in a single list. So determining the number
of members in a group should be a familiar task.

.. code-block:: python

    >>> len(members)
    5

:class:`~groupy.objects.Message`\ s, however, are a different matter. Since
there may be thousands of messages in a group, messages are returned in pages.
The default (and maximum) number of messages per page is 100. To determine the
total number of messages in a group, simply access the ``message_count``
attribute. Additional pages of messages can be obtained using 
:func:`~groupy.objects.MessagePager.older` and
:func:`~groupy.objects.MessagePager.newer`.

.. code-block:: python

    >>> len(messages)
    100
    >>> group.message_count
    3014
    >>> older = messages.older()
    >>> newer = messages.newer()

There are also methods for collecting a newer or older page of messages into
one list: :func:`~groupy.objects.MessagePager.iolder` and
:func:`~groupy.objects.MessagePager.inewer`. An example of using the former to
retrieve all messages in a group:

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> messages = group.messages()
    >>> while messages.iolder():
    ...       pass
    >>> len(messages) == group.message_count
    True

Often you'll want to post a new message to a group. New messages can be posted
to a group using its :func:`~groupy.objects.Group.post` method.

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
========

Unlike :class:`~groupy.objects.Group`\ s, :class:`~groupy.objects.Member`\ s,
and :class:`~groupy.objects.Bot`\ s, :class:`~groupy.objects.Message`\ s
*cannot* be listed directly. Instead, :class:`~groupy.objects.Message`\ s are
listed either from :class:`~groupy.objects.Group` or
:class:`~groupy.objects.Member` instances.

To list the messages from a group, use a group's 
:func:`~groupy.objects.Group.messages` method.

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> messages = group.messages()

To list the messages from a member, use a member's 
:func:`~groupy.objects.Member.messages` method.

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

.. note::

    Although the majority of messages will have just one attachment, there is
    no limit on the number of attachments. In fact, despite most clients being
    incapable of displaying them, the API doesn't even limit the number of each
    kind of attachment. For example, a single message might have two images,
    three locations, and one emoji.

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
:class:`~groupy.objects.Member` instances can be retrieved using the
:func:`~groupy.objects.Message.likes` method.

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
=======

:class:`~groupy.objects.Member` instances represent other GroupMe users.
Finding members can be accomplished in one of three ways.

Firstly, members may be listed from a group. This lists just the members of a
particular group.

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> members = group.members()

Secondly, members may be listed from a message. This lists just the members who
have "liked" a particular message.

.. code-block:: python

    >>> messages = group.messages()
    >>> message = message.newest
    >>> members = message.likes()

Lastly, *all* the members you've seen thus far can be listed directly.

.. code-block:: python

    >>> from groupy import Member
    >>> members = Member.list()

.. note::

    Although many attributes of a member are specific to a particular group,
    members listed in this fashion are taken from a single group with one
    exception: the nickname of each member listed from
    :func:`group.objects.Member.list` is the most frequent of the names that
    the member uses among the groups of which you are both members.

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


Groups and Members
==================

Members can be added and removed from groups. Adding one or multiple members to
a group is quite intuitive. The following examples assume that no one from
``group1`` is a member of ``group2`` (although the API doesn't care if you add
a member who is already a member).

.. code-block:: python
    
    >>> from groupy import Group
    >>> group1, group2 = Group.list()[:2]
    >>> member = group1.members().first
    >>> group2.add(member)

Multiple members can be added simultaneously as well. Suppose you wanted to add
everyone from ``group1`` to ``group2``.

.. code-block:: python

    >>> group2.add(*group1.members())

Removing members, however, must be done one at a time:
 
.. code-block:: python

    >>> for m in group2.members():
    ...   group2.remove(m)
    ... 

GroupMe and You
===============

One of the most basic pieces of information you'll want to obtain is your own!
**Groupy** makes this very simple:

.. code-block:: python

    >>> from groupy import User
    >>> your_info = User.get()

It contains your GroupMe profile/account information and settings: 

.. code-block:: python

    >>> print(your_info.user_id)
    12345678
    >>> print(your_info.name)
    Billy Bob <-- the MAN!
    >>> print(your_info.image_url)
    http://i.groupme.com/a01b23c45d56e78f90a01b12c3456789
    >>> print(your_info.sms)
    False
    >>> print(your_info.phone_number)
    +1 5055555555
    >>> print(your_info.email)
    bb@example.com

It also contains some meta information: 

.. code-block:: python

    >>> print(your_info.created_at)
    2011-3-14 14:11:12
    >>> print(your_info.updated_at)
    2013-4-20 6:58:26

``created_at`` and ``updated_at`` are returned as :class:`~datetime.datetime`
objects.


Bots
====

Bots can be a useful tool because each has a callback URL to which every
message in the group is POSTed. This allows your bot the chance to do... well,
something (whatever that may be) in response to every message!

.. note::

    Keep in mind that bots can only post messages to groups, so if anything
    else is going to get done, it'll be done by you, not your bot. That means
    adding and removing users, liking messages, direct messaging a member, and
    creating or modifying group will be done under your name.

Bot creation is simple. You'll need to give the bot a name and associate it
with a specific group. 

.. code-block:: python

    >>> from groupy import Bot, Group
    >>> group = Group.list().first
    >>> bot = Bot.create('R2D2', group)

``bot`` is now the newly created bot and is ready to be used. If you want, you
can also specify a callback URL *(recommened)*, as well as an image URL to be
used for the bot's avatar.

Just about the only thing a bot can do is post a message to a group. **Groupy**
makes it easy:

.. code-block:: python

    >>> from group import Bot
    >>> bot = Bot.list().first
    >>> bot.post("I'm a bot!")

Note that the bot always posts its messages to the group in which it belongs.
You can create multiple bots. Listing all of your bots is straightforward.

.. code-block:: python

    >>> from groupy import Bot
    >>> bots = Bot.list()

Now ``bots`` contains a list of all of your bots.

