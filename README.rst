======
Groupy
======

The simple yet powerful GroupMe API wrapper for Python 3.

Get the full documentation on `Read the Docs`_!

Installation
============

1) Login at ``https://dev.groupme.com/session/new``.
2) Click "Bots" menu button at the top.
3) Click "Click here to reveal" then copy your token.
4) Paste your token into ``~/.groupy.key``.
5) Copy ``Groupy/groupy`` into your package directory for ``Python3``.

Usage
=====

.. code-block:: python

    import groupy

    # list the groups you're in or the groups you're not in anymore
    groups = groupy.Group.list()
    former_groups = groupy.Group.list(former=True)

    # list the members in a group
    group = groups[0]
    members = group.members()
    
    # add and remove members from a group
    group2 = groups[1]
    group2.add(members[0])
    group2.remove(members[0])

    # list the 100 most recent messages in a group
    messages = group.messages()

    # older messages (and once in existence, newer ones as well) can be obtained easily.
    older_messages = messages.older()
    newer_messages = messages.newer()

    # collect all messages from a group
    all_messages = group.messages()
    while all_messages.iolder():
      pass

    # post a message to a group
    group.post('Hello world!')

    # include an image with the message
    img = groupy.Image.file(open('imagefilepath', 'rb'))
    group.post('Here is the pic you took :-)', img)

    # messages have either text, attachments, or both
    message = messages.newest
    print(message.text)
    for a in message.attachments:
      print(a)

    # ...and can be liked and unliked
    message.like()
    message.unlike()

    # list the members that liked a message
    for member in message.likes():
      print(member.nickname)

    # list the messages from another member (direct messages)
    members = group.members()
    member = members[0]
    direct_messages = member.messages()

    # post a message to another member (direct message)
    member.post('Hey are you available today?')

    # get information about yourself
    my = groupy.User.get()
    print(my.nickname)
    print(my.user_id)
    print(my.email)

Version History
===============

v0.4.0
- All known members can now be listed directly
- Re-wrote attachemnts classes

v0.3.1
------

- Fixed bug when adding members to a group
- Many additions to the docs

v0.3.0
------

- Liking/unliking works on direct messages
- Member instances can send and recieve direct messages
- Listing former groups now works correctly
- Listing groups and former groups is no longer limited to the first 500
- The direct message API now accepts the ``after_id`` parameter
- Documentation now on `Read the Docs`_!

v0.2.0
------

- Messages are returned in a message pager

v0.1.3
------

- Added class for representing a message attachment
- Fixed the automatic splitting of long texts

v0.1.2
------

- Fixed ``InvalidResponseError`` bug
- Updated documentation

v0.1.1
------
- Added basic documentation

v0.1.0
------
- Initial release

.. _Read the Docs: http://groupy.readthedocs.org/en/latest/
