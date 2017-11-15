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
to get done! It supports the entire API plus one or two undocumented features.

Groups
------
- list directly from the client
- create new groups
- destroy groups you own
- update group details
- join new groups
- rejoin former groups
- change group ownership

Members
-------
- list from a group
- add/remove from a group

Chats
-----
- list directly from the client

Messages
--------
- list from groups and chats
- post new messages to groups and chats
- like/unlike messages
- list gallery messages from a group
- list leaderboard messages from a group

User
----
- get/update your own information
- set/unset SMS mode

Blocks
------
- list from user
- block/unblock other users
- check if a block between you and another user exists
