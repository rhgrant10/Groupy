==============
Advanced Usage
==============

This part of the documentation contains explanations and examples of more
obscure aspects of **Groupy**.

Filter Lists
============

:class:`~groupy.object.listers.FilterList`\ s are exactly like the built-in
:class:`list` but with some convenient additions.

``first`` and ``last``
----------------------

``first`` and ``last`` are merely convenience properties. ``first`` corresponds
to the item at index ``0``, while ``last`` corresponds to the item at index
``-1``.

.. code-block:: python

    >>> from groupy.object.listers import FilterList
    >>> fl = FilterList(range(1, 11))
    >>> fl
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> fl.first
    1
    >>> fl.last
    10

One important difference, however, is when there are no elements in the list.

.. code-block:: python

    >>> fl = FilterList()
    >>> fl
    []
    >>> print(fl.first)
    None
    >>> fl[0]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    IndexError: list index out of range
    >>> print(fl.last)
    None
    >>> fl[-1]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    IndexError: list index out of range
    
Note that no exception is raised and ``None`` is returned instead.

``filter()``
------------

The :func:`~groupy.object.listers.FilterList.filter` method parses its keyword
arguments as filtering criteria. Only the items meeting all criteria are
returned.

The keywords correspond to object properties, but also indicate how to test the
relation to the value of the keyword argument. Thus a keyword-value pair such as
``name='Bob'`` would keep only those items with a ``name`` property equal to
``"Bob"``, whereas a pair like ``age__lt=20`` keeps only those items with an
``age`` property *less than* ``20``.

This is probably better explained with some simple examples.

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



Attachments
===========

Attachments are a common part of :class:`~groupy.object.responses.Message`\ s
and there are several different types. Currently, **Groupy** supports the
following types of attachments:

- :class:`~groupy.object.attachments.Location` - for locations
- :class:`~groupy.object.attachments.Image` - for images
- :class:`~groupy.object.attachments.Mentions` - for "@" mentions
- :class:`~groupy.object.attachments.Emoji` - for emoticons
- :class:`~groupy.object.attachments.Split` - for splitting bills\ [*]_

For all other types of attachments (such as those introduced in the future)
there exists a :class:`~groupy.object.attachments.GenericAttachment`.

.. [*] Split attachments are depreciated.

Types
-----

The section covers the various types of attachments and how to create them.

Locations
^^^^^^^^^

:class:`~groupy.object.attachments.Location` attachments are the simplest of all
attachment types. Each includes a ``name``, a latitude ``lat``, and a longitude
``lng``. Some location attachments also contain a ``foursqure_venue_id``.

.. code-block:: python

    >>> from groupy import attachments
    >>> loc = attachments.Location('My house', lat=34, lng=-84)
    >>> loc
    Location('My house', lat=34, lng=-84)
    >>> loc.name
    'My house'
    >>> loc.lat, loc.lng
    (34, -84)

Images
^^^^^^

:class:`~groupy.object.attachments.Image` attachments are unique in that they do
not actually contain the image data. Instead, they specify the URL from which
you can obtain the actual image. To create a new image from a local file object,
use the :func:`~groupy.object.attachments.Image.file` method.

.. code-block:: python

    >>> from groupy import attachments
    >>> image_attachment = attachments.Image.file(open(filename, 'rb'))
    >>> image_attachment
    Image(url='http://i.groupme.com/123456789')
    >>> image_attachment.url
    'http://i.groupme.com/123456789'

We can see that the image has been uploaded in exchange for a URL via the
GroupMe image service.

To fetch the actual image from an image attachment, simply use its
:func:`~groupy.object.attachments.Image.download` method. The image is returned
as a :class:`Pillow Image<PIL.Image.Image>`, so saving it to a file is simple.

.. code-block:: python

    >>> image_file = image_attachment.download()
    >>> image_file.save(filename)


Mentions
^^^^^^^^

:class:`~groupy.object.attachments.Mentions` are a new type of attachment and
have yet to be documented. However, they are simple to understand. Mentions
capture the details necessary to highlight "@" mentions of members in groups.
They contain a list of ``loci`` and an equal-sized list of ``user_ids``. Let's
find a good example to demonstrate mentions.

.. code-block:: python

    >>> from groupy import Group
    >>> message = None
    >>> mention = None
    >>> for g in Group.list():
    ...   for m in g.messages():
    ...     for a in m.attachments:
    ...       if a.type == 'mentions' and len(a.user_ids) > 1:
    ...         message = m
    ...         mention = a
    ...         break
    >>> message.text
    '@Bill hey I saw you with @Zoe Childs at the park!'
    >>> mention.user_ids
    ['1234567', '5671234']
    >>> mention.loci
    [[0, 5], [25, 11]]
    
As you can see, each element in ``loci`` has two integers, the first of which
indicates the starting index of the mentioning text, while second indicates its
length. The strings in ``user_ids`` correspond *by index* to the elements in
``loci``. You can use the ``loci`` to extract the mentioning portion of the
text, as well as obtain the mentioned member via ``user_ids``.

.. code-block:: python

    >>> for uid, (start, length) in zip(mention.user_ids, mention.loci):
    ...   end = start + length
    ...   uid, message.text[start:end]
    ...   member = message.group.members().filter(user_id=uid).first
    ...   member.uid, member.nickname
    ('1234567', '@Bill')
    ('1234567', 'Bill')
    ('5671234', '@Zoe Childs')
    ('5671234', 'Zoe Childs')


To create a mention, simply pass in a :class:`list` of user IDs and an
equally-sized :class:`list` of loci.

.. code-block:: python

    >>> from groupy.attachments import Mentions
    >>> Mentions(['1234567', '2345671'], [[0, 4], [5, 3]])
    Mentions(['1234567', '2345671'])


Emojis
^^^^^^

Emojis are relatively undocumented but frequently appear in messages. More
documentation will come as more is learned.

Emoji attachments have a ``placeholder`` and a ``charmap``. The ``placeholder``
is a high-point or unicode character designed to mark the location of the emoji
in the text of the message. The ``charmap`` serves as some sort of translation
or lookup tool for obtaining the actual emoji.

Splits
^^^^^^

.. note::

    This type of attachment is depreciated. They were part of GroupMe's bill
    splitting feature that seems to no longer be implemented in their clients.
    **Groupy**, however, still supports them due to their presence in older
    messages.

:class:`~groupy.object.attachments.Split` attachments have a single attribute:
``token``.


Sending Attachments
-------------------

To send an attachment along with a message, simply append it to the
:func:`~groupy.object.responses.Recipient.post` method as another argument.

.. code-block:: python

    >>> from groupy import Group
    >>> from groupy.attachment import Location
    >>> loc = Location.create('My house', lat=33, lng=-84)
    >>> group = Group.list().first
    >>> group.post("Hey meet me here", loc)

If there are several attachments you'd like to send in a single message, simply
keep appending them!

.. code-block:: python

    >>> from groupy.attachment import Image
    >>> img = Image.file('front-door.png')
    >>> group.post("I said meet me here!", loc, img)

Alternatively, you can collect multiple attachments into an
:class:`iterable<collections.abc.Iterable>`.

.. code-block:: python

    >>> attachments = [img, loc]
    >>> group.post("Are you listening?", *attachments)
