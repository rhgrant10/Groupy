"""
.. module:: attachments
    :platform: Unix, Windows
    :synopsis: A module containing all attachment classes

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

This module contains classes for the different types of attachments.

"""
from ..api import endpoint


class Attachment:
    """Base class for attachments.

    :param str type_: the type of the attachment
    """
    def __init__(self, type_):
        self.type = type_

    def as_dict(self):
        """Return the attachment as a dictionary.

        :returns: the attachment as a dictionary
        :rtype: :class:`dict`
        """
        return self.__dict__


class GenericAttachment(Attachment):
    """A generic attachment.

    This attachment accepts any keyword arguments, but must be given a
    particular type.

    :param str type: the type of attachment
    """
    def __init__(self, type, **kwargs):
        super().__init__(type)
        for k, v in kwargs.items():
            setattr(self, k, v)


class Image(Attachment):
    """An image attachemnt.

    Image attachments do not contain an image. Instead, they specify a URL from
    which the image can be downloaded and must have a domain of
    "i.groupme.com". Such URLs are known as "i" URLs, and are from the GroupMe
    image service.

    .. note::

        Use the direct initializer *if and only if* the image already has a
        known GroupMe image service URL. Otherwise, use the
        :func:`~groupy.object.attachments.Image.file` method.

    :param str url: the URL at which the image can be fetched from the GroupMe
        image service
    :param str source_url: the original URL of the image (optional)
    """
    def __init__(self, url, source_url=None):
        super().__init__('image')
        self.url = url
        self.source_url = source_url

    def __repr__(self):
        return "Image(url={!r})".format(self.url)

    @classmethod
    def file(cls, image):
        """Upload an image file and return it as an attachment.

        :param image: the file containing the image data
        :type image: :class:`file`
        :returns: an image attachment
        :rtype: :class:`~groupy.object.attachments.Image`
        """
        return cls(endpoint.Images.create(image)['url'])

    def download(self):
        """Download the image data of the image attachment.

        :returns: the actual image the image attachment references
        :rtype: :class:`PIL.Image.Image`
        """
        return endpoint.Images.download(self.url)


class Location(Attachment):
    """An attachment that specifies a geo-location.

    In addition to latitude and longitude, every location attachment also
    specifies a name. Some (especially older) location attachments also contain
    a ``foursquare_venue_id`` attribute.

    :param str name: the location name
    :param float lat: the latitude
    :param float lng: the longitude
    :param str foursquare_venue_id: the FourSquare venue ID (optional)
    """
    def __init__(self, name, lat, lng, foursquare_venue_id=None):
        super().__init__('location')
        self.name = name
        self.lat = lat
        self.lng = lng
        self.foursquare_venue_id = foursquare_venue_id

    def __repr__(self):
        return "Location(name={!r}, lat={!r}, lng={!r})".format(
                self.name, self.lat, self.lng)


class Emoji(Attachment):
    """An attachment containing emoticons.

    Emoji attachments do not contain any emoticon images. Instead, a
    placeholder specifies the location of the emoticon in the text, and a
    ``charmap`` facilitates translation into the emoticons.

    :param str placeholder: a high-point/invisible character indicating the
        position of the emoticon
    :param list charmap: a list of lists containing pack IDs and offsets
    """
    def __init__(self, placeholder, charmap):
        super().__init__('emoji')
        self.placeholder = placeholder
        self.charmap = charmap

    def __repr__(self):
        return "Emoji(placeholder={!r}, charmap={!r})".format(
            self.placeholder, self.charmap)


class Split(Attachment):
    """An attachment containing information for splitting a bill.

    This type of attachment is depreciated. However, such attachments are still
    present in older messages.

    :param str token: the token that splits the bill
    """
    def __init__(self, token):
        super().__init__('split')
        self.token = token

    def __repr__(self):
        return "Split(token={!r})".format(self.token)


class Mentions(Attachment):
    """An attachment that specifies "@" mentions.

    Mentions are a new addition to the types of attachments. Each contains two
    parallel lists: ``user_ids`` and ``loci``. The elements in ``loci`` specify
    the start index and length of the mention, while the elements in
    ``user_ids`` specify by user_id which user was mentioned in the
    corresponding element of ``loci``.

    .. note::

        The length of ``user_ids`` must be equal to the length of ``loci``!

    :param list user_ids: a list of user IDs
    :param list loci: a list of ``(start, length)`` elements
    """
    def __init__(self, user_ids, loci=None):
        super().__init__('mentions')
        self.user_ids = user_ids
        self.loci = loci

    def __repr__(self):
        return "Mentions({!r})".format(self.user_ids)


class AttachmentFactory:
    """A factory for creating attachments from dictionaries.
    """
    _factories = {
        'image': Image,
        'location': Location,
        'emoji': Emoji,
        'mentions': Mentions,
        'split': Split
    }

    @classmethod
    def create(cls, **kwargs):
        """Create and return an attachment.

        :param str type: the type of attachment to create; if unrecognized, a
            generic attachment is returned
        :returns: a subclass of :class:`~groupy.object.attachments.Attachment`
        """
        t = kwargs.pop('type', None)
        try:
            return cls._factories[t](**kwargs)
        except (TypeError, KeyError):
            # Either kwargs contianed an unexpected keyword for attachment type
            # t, or t is not a known attachment type
            return GenericAttachment(t, **kwargs)
