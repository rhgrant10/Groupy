Groupy
======

Installation
------------

1) Go to `dev.groupme.com`, click the `Applications` menu button, then click
"Looking for your access token?" Copy and paste your token into `~/.groupy.key`.

2) Copy `Groupy/groupy` into your package directory for `Python3`.

Usage
-----

.. code-block:: python

    >>> import groupy
    >>> groups = groupy.Group.list()
    >>> e8s = groups.filter(name__contains='E8')
    >>> len(e8s)
    2
    >>> a, b = e8s
    >>> x = e8s.first
    >>> assert a == x
    >>> members = x.members()
    >>> muted = members.filter(muted=True)
    >>> for m in muted.sort('nickname'):
    ...   print(m)
    Bob (0xb0b501337 - L8 - Kirkwood/Edgewood)
    Rob (rhgrant10 - L14 - Norcross)
    ...
    >>> messages = x.messages()
    >>> len(messages)
    100
    >>> likes = messages.first.likes()
    >>> len(likes)
    1
    >>> for m in likes:
    ...   print(m)
    Rob (rhgrant10 - L14 - Norcross)
    >>> print(messages.first.text)
    "Hey Bob, do you like my API wrapper?"
    >>> me = groupy.User.get()
    >>> print(me)
    Rob (rhgrant10 - L14 - Norcross)
    >>> # etc, etc...
    
 
