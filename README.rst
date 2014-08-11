Groupy
======

A simple yet powerful GroupMe API wrapper for Python 3.

Installation
------------

1) Login at ``https://dev.groupme.com/session/new``
2) Click "Bots" menu button at the top
3) Click "Click here to reveal"
4) Copy and paste your token into ``~/.groupy.key``.
5) Copy ``Groupy/groupy`` into your package directory for ``Python3``.

Usage
-----

.. code-block:: python

    >>> import groupy
    >>> groups = groupy.Group.list()
    >>> gs = groups.filter(name__contains='something')
    >>> len(gs)
    2
    >>> a, b = gs
    >>> x = gs.first
    >>> assert a == x
    >>> members = x.members()
    >>> len(members)
    51
    >>> x.max_members
    100
    >>> muted = members.filter(muted=True)
    >>> for m in muted.sort('nickname'):
    ...   print(m)
    Bill
    Rob
    Tom
    >>> x.message_count
    32512
    >>> messages = x.messages()
    >>> len(messages)
    100
    >>> likes = messages.first.likes()
    >>> len(likes)
    2
    >>> for m in likes:
    ...   print(m)
    Jane
    Tom
    >>> print(messages.first.text)
    I'm working on it too! :-)
    >>> me = groupy.User.get()
    >>> print(me)
    Joe
    >>> # etc, etc...
    
