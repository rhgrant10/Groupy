============
Introduction
============

About GroupMe
=============

GroupMe is a messaging app that allows you to create groups and have others
join them with you. In addition to group messaging, fellow group members can be
messaged directly. GroupMe is available for most platforms, lets you share
links, images, and locations, and messages can be favorited (or "liked"). You
can read more `about GroupMe`_, but the best part about it is that they provide
an API!

.. _about GroupMe: http://groupme.com

The GroupMe API is documented, but there are some notable omissions. Many of
the properties of groups and messages are not documented, and some features are
only hinted at by the documentation. Regardless, all of the information about
your groups, their members, their messages, you, and your bots can be obtained
through the GroupMe API. You can `read the API documentation`_ for more (or
less) detailed information.

.. _read the API documentation: http://dev.groupme.com

About **Groupy**
================

**Groupy** lets you forget about the GroupMe API and focus on what you need
to get done! 

It is composed of two main parts:

.. hlist::

    * API wrapper (:mod:`groupy.api`)
    * Object abstraction (:mod:`groupy.object`)


Current Features
----------------

Groups
^^^^^^

- Create, update, and destroy your own groups
- List and filter your current and former groups
- Add and remove members from your current groups
- List and filter group members
- List and filter group messages

Members
^^^^^^^

- List and filter all known members
- List and filter direct messages
- Post direct messages to members

Messages
^^^^^^^^

- Collect all messages from a group or member
- Like and unlike messages (even direct messages!)
- List and filter members who liked a message
- Inspect and create attachments

Bots
^^^^

- List and filter your bots
- Use your bots to post messages
- Create, update, and destroy bots

Users
^^^^^

- Get your user information
- Enable and disable SMS mode

Planned Development
-------------------

(in no particular order)

- Unit tests
- Installation via pip
- More direct way to add and remove yourself from groups
- Remove multiple members in one method call
- Porcelain for checking results of adding members
- Automatic updating of object attributes without the need to re-fetch objects
- Member objects that are aware of membership in all groups
- Additional ways to access objects
- More convenience methods instead of accessing API attributes directly
- Documentation about the API wrapper package
- Python 2.7 support