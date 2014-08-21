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
a name, a latitude, and a longitude. Some location attachments also contain a
``foursqure_venue_id``.

.. code-block:: python

	>>> from groupy import attachments
	>>> loc = attachments.Location.create('My house', lat=34, lng=-84.3)


Images
^^^^^^

Image attachments are unique in that they do not actually contain the image
data. Instead, they specify the URL from which you can obtain the actual image.
To create a new image from a local file object, use the
:func:`~groupy.object.attachments.Image.file` method.

.. code-block:: python

	>>> from groupy import attachments
	>>> img_a = attachments.Image.file(open(filename, 'rb'))
	>>> img_a
	Image(url='http://i.groupme.com/a01b23c45d56e78f90a01b12c3456789')

We can see that the image has been uploaded in exchange for a URL via the
GroupMe image service.

To fetch the actual image from an image attachment, simply use its
:func:`groupy.object.attachment.Image.download` method. The image is returned as
a :class:`PIL.Image.Image`, so saving it to a file is very easy.

.. code-block:: python

	>>> img_f = img_a.download()
	>>> img_f.save(filename)


Mentions
^^^^^^^^

Mentions are a new type of attachment and have yet to be documented. However,
they are simple to understand.

Mentions capture the details necessary to highlight "@" mentions of members in
groups. They contain a list of ``loci`` and an equal-sized list of ``user_ids``.
Let's find a good example to demonstrate mentions.

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
	>>> for uid, locus in zip(mention.user_ids, mention.loci):
	...   uid, message.text[locus[0]:sum(locus)]
	...
	('1234567', '@Bill')
	('5671234', '@Zoe Childs')
	

Emojis
^^^^^^

Emojis are relatively undocumented but frequently appear in messages. More
documentation will come as more is learned.

Splits
^^^^^^

Although this type of attachment is undocumented, it is also depreciated. It was
part of GroupMe's bill splitting feature that no longer appears in their
clients. **Groupy**, however, still supports them due to their presence in older
messages.

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
	>>> group.post("Hey meet me here", loc, img)

Alternatively, you can collect them into a :class:`tuple` or a :class:`list`.

.. code-block:: python

	>>> attachments = [img, loc]
	>>> group.post("Hey meet me here", *attachments)

