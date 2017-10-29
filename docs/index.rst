==================
Welcome to Groupy!
==================

.. image:: https://img.shields.io/pypi/v/GroupyAPI.svg
    :target: https://pypi.python.org/pypi/GroupyAPI

.. image:: https://travis-ci.org/rhgrant10/Groupy.svg?branch=dev
    :target: https://travis-ci.org/rhgrant10/Groupy

.. image:: https://readthedocs.org/projects/groupy/badge/?version=latest
    :target: https://groupy.readthedocs.org/en/latest

The simple yet powerful wrapper for the GroupMe API.


.. code-block:: console

    $ python3 -m pip install GroupyAPI

.. code-block:: python

    >>> from groupy.client import Client
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


Table of Contents
=================

.. toctree::
    :maxdepth: 2

    pages/introduction
    pages/installation
    pages/quickstart
    pages/advanced
    pages/contributing
    pages/api
    pages/changelog