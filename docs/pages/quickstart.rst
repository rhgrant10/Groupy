==========
Quickstart
==========

This page gives an overview of all but the most advanced features of **Groupy**.

First, you'll want to make sure that 

- **Groupy** is *installed*
- **Groupy** can *find your API key*

See the :doc:`installation` page for instructions. Now that that's out of the
way, let's get started!

List Groups
===========

The starting point for everything is to obtain a list of groups.

First, of course, we must import the Groupy module:

.. code-block:: python

    >>> import groupy

Now let's list your groups:

.. code-block:: python

    >>> groups = groupy.Group.list()

The ``groups`` list acts just like the regular Python :class:`list`, but has
some additional features as well. Let's take a look.

    >>> group = groups.first
    >>> group = groups.last

These are merely convenience properties, but are used throught the
documentation.

List Messages
=============

Now that we have a group, we can list the messages it contains.

.. code-block:: python

    >>> messages = group.messages()

We can work with the list of messages in the same way that we can work with
lists of groups.

.. code-block:: python

    >>> message = messages.first
    >>> message = messages.last

But that can be rather misleading, since (usually) the first message in the list
is actually the newest! That's okay, because lists of messages have two
additional properties to make sense of the situation.

.. code-block:: python

    >>> message = messages.oldest
    >>> message = messages.newest

More Messages
=============

The number of messages in a group can be obtained directly from the group.

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> group.message_count
    1348

As you can see, this group contains 1348 messages. If you attempt to obtain the
number of messages in a group by obtaining the length of the list of messages,
you'll probably find they're not equal.

.. code-block:: python

    >>> group.message_count == len(group.messages())
    False

That's because messages are returned in pages since there may be thousands. By
default, :func:`~groupy.objects.Recipient.messages` returns the most recent
page of messages. The default (and maximum) page size is 100.

Retrieving more messages is simple. Message pages can fetch the next and
previous pages.

.. code-block:: python

    >>> older = messages.older()
    >>> newer = messages.newer()

Now there are 3 pages worth of messages\ [#]_\ . But clearly, seperate pages of
messages are difficult to work with. There's an easier way.

.. code-block:: python

    >>> while messages.iolder():
    ...   pass
    ... 

Presto\ [#]_\ ! Now ``messages`` contains *every* message in the group.

.. code-block:: python

    >>> group.message_count == len(messages)
    True

The :func:`~groupy.objects.MessagePager.inewer` method is just like
:func:`~groupy.objects.MessagePager.newer` except that it operates "in-place"
and extends the list on which it was invoked intelligently such that the
messages in the list are in a consistent temporal order. The "in-place" version
returns ``True`` if the list was extended, and ``False`` otherwise.

One common task is to check whether there are new messages.
:func:`~groupy.objects.MessagePager.inewer` makes this a trivial task.

.. code-block:: python

    >>> if messages.inewer():
    ...   # Hey, we have new messages!
    ... else:
    ...   # No newer messages than the newest message in 'messages'
    ... 

Of course, there is more than one way to skin a cat! The following method may
work better if you need to process *just* the new messages, whereas the method
above would work better for situations in which the entire message history must
be repeatedly processed.

.. code-block:: python

    >>> new_messages = messages.newer()
    >>> if new_messages:
    ...   # Hey, we have new messages.
    ... else:
    ...   # Man... this group is quiet!
    ... 

.. [#] In reality, there may not be any messages newer than those in
   ``messages``, in which case ``newer`` would be ``None``, but let's ignore
   those details for the time being.

.. [#] It may take a while, depending on your connection speed and number of
    messages in the group.

Messaging
=========

You'll probably often want to send a message. **Groupy** makes this easy.

.. code-block:: python

    >>> from groupy import Group
    >>> group = Group.list().first
    >>> group.post("Hello group")

Super easy, right? What about messaging a member? Also super easy:

.. code-block:: python

    >>> member = group.members().first
    >>> member.post("Hello person")

Likes
=====

There is another fact of life we must face: sometimes you like messages. We all
do it... how hard can it be? Not that hard:

.. code-block:: python

    >>> message = group.messages().first
    >>> message.like()

Now what if we decided we made a mistake and don't like the message afterall?
Also not a problem:

.. code-block:: python

    >>> message.unlike()

Note that both :func:`~groupy.objects.Message.like` and
:func:`~groupy.objects.Message.unlike` return ``True`` if the action was
successful:

.. code-block:: python

    >>> if message.like():
    ...   # Success!
    ... else:
    ...   # Uh-oh...
    ...

What about finding out who has already liked a message? Likes are reported
conveniently as a list of members:

.. code-block:: python

    >>> favorited_by = message.likes()

Now ``favorited_by`` is a list of the members who liked the message. This means
that counting likes is a simple matter of finding the length of
``favorited_by``:

.. code-block:: python

    >>> num_likes = len(favorited_by)


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

