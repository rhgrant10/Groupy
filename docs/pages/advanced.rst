==============
Advanced Usage
==============

This part of the documentation contains explanations and examples of more
complex aspects of **Groupy**.

Attachments
===========

:class:`~groupy.objects.Message`\ s can contain various types of
:class:`~groupy.objects.Attachment`\ s. Currently, **Groupy** supports
the following types of attachments:

- :class:`~groupy.objects.Image` - for images
- :class:`~groupy.objects.Location` - for locations
- :class:`~groupy.objects.Split` - [*]_
- :class:`~groupy.objects.Emoji` - for emoticons
- :class:`~groupy.objects.Mentions` - for "@" mentions

.. [*] This type of attachment will be depreciated soon.

Each of these classes has a :func:`create` method that accepts arguments
specific to it's class.

Types
-----

Locations
^^^^^^^^^

Location attachments are the simplest of all attachment types. Each includes
a name, a latitude, and a longitude.

.. code-block:: python

	>>> loc = groupy.Location.create('My house', lat=34, lng=-84.3)

Some location attachments also contain a ``foursqure_venue_id``.

Images
^^^^^^

Image attachments are unique in that they do not actually contain the image
data.

Emojis
^^^^^^

Emojis are relatively undocumented but frequently appear in messages.

Mentions
^^^^^^^^

Mentions are a new type of attachment and is yet undocumented.

Splits
^^^^^^

This type of attachment is not only largely undocumented, it is depreciated.
