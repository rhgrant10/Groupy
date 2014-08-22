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

The most basic operation is listing things.
:class:`~groupy.object.responses.Group`\ s,
:class:`~groupy.object.responses.Member`\ s, and
:class:`~groupy.object.responses.Bot`\ s can be listed directly.

.. code-block:: python

    >>> import groupy
    >>> groups = groupy.Group.list()
    >>> members = groupy.Member.list()
    >>> bots = groupy.Bot.list()

The object lists are returned as a 
:class:`~groupy.object.listers.FilterList`\ . These behave just like the
built-in :class:`list` does with some convenient functionality:
:obj:`~groupy.object.listers.FilterList.first` and
:obj:`~groupy.object.listers.FilterList.last`.

.. code-block:: python

    >>> groups.first == groups[0]
    True
    >>> groups.last == groups[-1]
    True

The most useful feature of a  :class:`~groupy.object.listers.FilterList`\ ,
however, is its :func:`~groupy.object.listers.FilterList.filter` method. It
parses whatever keyword arguments are passed to it and filters the list such
that only the items meeting all criteria are included. The keywords correspond
to object properties, but also indicate how to test the relation to the value
of the keyword argument. Thus a keyword-value pair such as ``name='Bob'`` would
keep only those items with a ``name`` property equal to ``"Bob"``, whereas a
pair like ``age__lt=20`` keeps only those items with an ``age`` property *less
than* ``20``.

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

From a :class:`~groupy.object.responses.Group`, you can list its 
:class:`~groupy.object.responses.Member`\ s and
:class:`~groupy.object.responses.Message`\ s.

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

:class:`~groupy.object.responses.Message`\ s, however, are a different matter.
Since there may be thousands of messages in a group, messages are returned in
pages. The default (and maximum) number of messages per page is 100. To
determine the total number of messages in a group, simply access the
``message_count`` attribute. Additional pages of messages can be obtained using
:func:`~groupy.object.listers.MessagePager.older` and
:func:`~groupy.object.listers.MessagePager.newer`.

.. code-block:: python

    >>> len(messages)
    100
    >>> group.message_count
    3014
    >>> older = messages.older()
    >>> newer = messages.newer()

There are also methods for collecting a newer or older page of messages into
one list: :func:`~groupy.object.listers.MessagePager.iolder` and
:func:`~groupy.object.listers.MessagePager.inewer`. An example of using the
former to retrieve all messages in a group:

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> messages = group.messages()
    >>> while messages.iolder():
    ...       pass
    ... 
    >>> len(messages) == group.message_count
    True

Often you'll want to post a new message to a group. New messages can be posted
to a group using its :func:`~groupy.object.responses.Recipient.post` method.

.. code-block:: python

    >>> from group import Group
    >>> group = Group.list().first
    >>> group.post('Hello to you')
    >>> group.messages().newest.text
    'Hello to you'

.. note::

    Posting a message does not affect ``message_count``. However, retrieving
    any page of messages *does* update it.

:class:`~groupy.object.responses.Group`\ s have many attributes, some of which
can be changed.

.. code-block:: python

    >>> group.name
    'My Family'
    >>> group.image_url
    'http://i.groupme.com/123456789'
    >>> group.description
    'Group of my family members - so we can keep up with each other.'
    >>> group.update(name="My Group of Family Members")
    >>> group.name
    'My Group of Family Members'
    >>> group.update(name="[old] Family Group", description="The old family group")
    >>> group.name
    '[old] Family Group'
    >>> group.description
    'The old family group'

Some :class:`~groupy.object.responses.Group`\ s also have a ``share_url`` that
others can visit to join the group.

.. code-block:: python

    >>> group.share_url
    'https://groupme.com/join_group/1234567890/SHARE_TOKEN'

Beware that not every group is created with a share link, in which case the
value of ``share_url`` would be ``None``. However, this can be changed in the
same way as other group information.

.. code-block:: python

    >>> print(group.share_url)
    None
    >>> group.update(share=True)
    >>> group.share_url
    'https://groupme.com/join_group/1234567890/SHARE_TOKEN'

.. note::

    The ``SHARE_TOKEN`` is specific to each group's share link.

The remainder of a :class:`~groupy.object.responses.Group`\ s aattributes cannot
be changed. Some more important ones are shown below.

.. code-block:: python

    >>> group.group_id
    '1234567890'
    >>> group.creator_user_id
    '0123456789'
    >>> print(group.created_at)
    2013-12-25 9:53:33
    >>> print(group.updated_at)
    2013-12-26 4:21:08


Messages
========

Unlike :class:`~groupy.object.responses.Group`\ s,
:class:`~groupy.object.responses.Member`\ s, and
:class:`~groupy.object.responses.Bot`\ s,
:class:`~groupy.object.responses.Message`\ s *cannot* be listed directly.
Instead, :class:`~groupy.object.responses.Message`\ s are listed either from
:class:`~groupy.object.responses.Group` or
:class:`~groupy.object.responses.Member` instances.

To list the messages from a group, use a group's 
:func:`~groupy.object.responses.Recipient.messages` method.

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> messages = group.messages()

To list the messages from a member, use a member's 
:func:`~groupy.object.responses.Recipient.messages` method.

.. code-block:: python

    >>> from groupy import Member
    >>> member = Member.list().first
    >>> messages = member.messages()

Messages have several properties. Let's look at a few of them. Messages have a
timestamp indicating when the message was created as a
:class:`datetime.datetime` instance, as well as information about the member
who posted it. Of course, messages can have text and attachments. 

.. code-block:: python

    >>> message = messages.newest
    >>> print(message.created_at)
    2014-4-29 12:19:05
    >>> message.user_id
    '0123456789'
    >>> message.name
    'Kevin'
    >>> message.avatar_url
    'http://i.groupme.com/123456789'
    >>> message.text
    'Hello'
    >>> message.attachments
    [Image(url='http://i.groupme.com/123456789')]

.. note::

    Not every message will have text and not every message will have
    attachments but every message must have one or the other.

.. note::

    Although the majority of messages will have just one attachment, there is
    no limit on the number of attachments. In fact, despite that most clients
    are incapable of displaying more than one of each type of attachment, the
    API doesn't limit the types of attachments in any way. For example, a
    single message might have two images, three locations, and one emoji, but
    it's not likely that any client would show them all or handle the message
    without error.

There are multiple types of messages. System messages are messages that are not
sent by a member, but generated by member actions. Many things generate system
messages, including membership changes (entering/leaving, adding/removing),
group updates (name, avatar, etc.), and member updates (nickname, avatar,
etc.), and changing the topic.

Additionally there are group messages and direct messages. Group messages are
messages in a group, whereas direct messages are messages between two members.

Each message has a few properties that can be used to differentiate among the
types.

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
:class:`~groupy.object.responses.Member` instances can be retrieved using the
:func:`~groupy.object.responses.Message.likes` method.

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

:class:`~groupy.object.responses.Member` instances represent other GroupMe
users. Finding members can be accomplished in one of three ways.

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
    :func:`~groupy.object.responses.Member.list` is the most frequent of the
    names that the member uses among the groups of which you are both members.

Each member has a user ID, a nickname, and a URL indicating their avatar image
that are specific to the group from which the member was listed.

.. code-block:: python

    >>> member = members.first
    >>> member.user_id
    '0123456789'
    >>> member.nickname
    'Bill'
    >>> member.avatar_url
    'http://i.groupme.com/123456789'

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
    http://i.groupme.com/123456789
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

