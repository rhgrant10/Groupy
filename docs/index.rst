======
Groupy
======

.. image:: https://img.shields.io/pypi/v/GroupyAPI.svg
    :target: https://pypi.python.org/pypi/GroupyAPI

.. image:: https://travis-ci.org/rhgrant10/Groupy.svg?branch=dev
    :target: https://travis-ci.org/rhgrant10/Groupy

.. image:: https://readthedocs.org/projects/groupy/badge/?version=latest
    :target: https://groupy.readthedocs.org/en/latest

The simple yet powerful API client for the GroupMe messaging service.


.. code-block:: console

    $ python3 -m pip install GroupyAPI


.. code-block:: python

    >>> from groupy import Client
    >>> client = Client.from_token('api_token')
    
    >>> groups = list(client.groups.list().autopage())

    >>> for group in groups:
    ...     print(group.name)
    
    >>> group = groups[0]
    >>> for member in group.members:
    ...     print(member.nickname)

    >>> for message in group.messages.list().autopage():
    ...     print(message.text)
    ...     for attachment in message.attachments:
    ...         print(attachment.type)
    ...     if 'love' in message.text.lower():
    ...         message.like()



Features
========

**Groupy** supports the entire GroupMe API... plus one or two undocumented
features.

- list current and former groups
- create, update, and destroy groups
- list group and chat messages
- access group leaderboards and galleries
- post new messages to groups and chats
- upload images for use as attachments
- download image attachments
- add, remove, and list group members
- like and unlike messages
- access your user account details
- update your SMS mode settings
- block and unblock other users
- post messages as a bot
- create, list, update, and destroy bots
- list chats with other users
- join new groups and rejoin former groups 
- transfer group ownership


Table of Contents
=================

.. toctree::
    :maxdepth: 3

    pages/installation
    pages/quickstart
    pages/api
    pages/contributing
    pages/changelog


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

