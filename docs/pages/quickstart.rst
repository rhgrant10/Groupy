==========
Quickstart
==========

Who Am I?
=========

One of the most basic pieces of information you'll want to obtain is your own!
Groupy makes this very simple:

.. code-block:: python

    >>> from groupy import User
    >>> your = User.get()
    >>> print(your.nickname)
    Fred
    >>> print(your.user_id)
    1234567890
    >>> print(your.email)
    fred.no@email.com
    >>> 

The Order of Things
===================

Not all objects are reported equally! For example, although you can list all of
your groups, there is *no direct way* to list all of the members. This is
because of the way in which the API is structured. Don't worry, it's not
complicated, but some find it surprising, so we'll just get this part out of
the way!

Groups are the starting point for everything.

Members are listed from groups. There is no global members list! The API
doesn't know about members that are not in at least one of the groups you're in
currently or were in previously. In other words, if you've never "seen" the
member in a group, you'd have to know their user id upfront to direct message
them or add them to a group.

Group messages are listed from groups, and direct (personal) messages are
listed from (you guessed it) members. Messages come in pages, with the most
recent page being the default page. Groupy has an easy way to page through the
messages or to collect an entire message history.

Fetching Stuff
==============

Mainly, you'll want to get a list of groups, messages, or members. With Groupy,
this is easy:

.. code-block:: python

    from groupy import Group

    # List current groups
    groups = Group.list()

    # List the members and messages of a single group
    group = groups[0]
    members = group.members()
    messages = group.messages()

Now ``members`` contains all the members of ``group``, and ``messages`` 
contains the most recent page of messages in ``group``. Messages can also be
listed from a member:

.. code-block:: python

    member = members[0]
    direct_messages = member.messages()

Now ``direct_messages`` contains the most recent page of messages between you
and ``member``. Easy right? But what if you wanted to get older messages? Well,
that's easy too:

.. code-block:: python

    older_messages = messages.older()

``older_messages`` now contains the page of messages that preceeds
``messsages``. In other words, the newest message in ``older_messages``
immediately preceeds the oldest message in ``messages``. This can be checked
quite easily with Groupy:

.. code-block:: python

    # Make a "timeline" using the oldest and newest messages from each page.
    timeline = [older_messages.oldest, older_messages.newest,
                messages.oldest, messages.newest]
    
    # Define a function to pluck timestamp information from a message.
    def get_timestamp(msg):
        return msg.created_at

    # Map the function to the timeline.
    timestamps = list(map(get_timestamp, timeline))

    # This should not raise an AssertionError!
    assert sorted(timeline) == timeline

But what if we wanted to get all of the messages since the beginning of a
group? Well, that's also easy:

.. code-block:: python

    # Get the most recent page of messages.
    messages = group.messages()

    # Extend the page with additional pages of messages.
    while messages.iolder():
        pass

It may take a while, depending on your connection speed and number of messages
in the group, but now ``messages`` contains all of the messages from the group.
:func:`iolder<groupy.objects.Message.iolder>` is the "in-place" version of
:func:`older<groupy.objects.Message.older>`, and works by fetching the page of
messages that preceeds the oldest message it has and adding them to the list
in-place.

Lastly, :func:`older<groupy.objects.Message.older>` and 
:func:`iolder<groupy.objects.Message.iolder>` have counter-parts
:func:`newer<groupy.objects.Message.newer>` and
:func:`inewer<groupy.objects.Message.inewer>` for fetching newer messages. That
means checking for new messages is as easy as:

.. code-block:: python

    messages = group.messages()
    count = len(messages)

    messages.inewer()
    if len(messages) > count:
        # New messages have arrived... do stuff

Messaging
=========

Let's face it: sometimes we just want to send a message. Messages can be sent
to both groups and members! To message a group:

.. code-block:: python

    group.post("Hello world")

Super easy, right? What about messaging a member? Also easy:

.. code-block:: python

    member.post("Hello... person")

There is another fact of life we must face: sometimes you like messages. We all
do it; how hard can it be? Not hard:

.. code-block:: python

    message.like()

What if we made a mistake and decide we don't like the message after all? Not
a problem:

.. code-block:: python

    message.unlike()

Note that both :func:`like<groupy.objects.Message.like>` and
:func:`unlike<groupy.objects.Message.unlike>` return ``True`` if the action was
successful:

.. code-block:: python

    if message.like():
        # success
    else:
        # Uh-oh...

What about finding out who has already liked a message? Likes are reported as
a list of members:

.. code-block:: python

    favorited_by = message.likes()

Now ``favorited_by`` is a list of the members who liked the message. 

Groups and Members
==================

Members can be added and removed from groups. Adding one or multiple members to
a group is quite intuitive:

.. code-block:: python
    
    # Add one member
    group.add(member)

    # Add several members
    group.add(*members)

Removing members is done one at a time: 
 
.. code-block:: python

    # Remove one member
    group.remove(member)

    # Remove several members
    for m in members:
      group.remove(m)

