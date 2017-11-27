from . import base
from groupy import utils


# use a class registry to enable factory creation of attachment objects
class AttachmentMeta(type):
    _types = {}

    def __init__(cls, name, bases, attrs):
        cls._types[name.lower()] = cls


class Attachment(base.Resource, metaclass=AttachmentMeta):
    """Base attachment class.

    Every attachment has a type and additional data.

    :param str type: attachment type
    :param kwargs data: additional attachment data
    """

    def __init__(self, type, **data):
        data['type'] = type
        self.data = data

    def to_json(self):
        """Return the attachment as JSON serializable dict.

        :return: serializable attachment data
        :rtype: dict
        """
        return self.data

    @classmethod
    def from_data(cls, type, **data):
        """Create an attachment from data.

        :param str type: attachment type
        :param kwargs data: additional attachment data
        :return: an attachment subclass object
        :rtype: `~groupy.api.attachments.Attachment`
        """
        try:
            return cls._types[type](**data)
        except KeyError:
            return cls(type=type, **data)

    @classmethod
    def from_bulk_data(cls, attachments):
        """Create multiple attachments from a list of attachment data.

        :return: attachment sublcass objects
        :rtype: :class:`list`
        """
        return [cls.from_data(**a) for a in attachments]


class Location(Attachment):
    """A location attachment.

    :param float lat: latitude
    :param float lng: longitude
    :param str name: the name
    :param str foursqure_venue_id: an optional Foursquare venue ID
    """

    def __init__(self, lat, lng, name, foursqure_venue_id=None):
        super().__init__(type='location', lat=lat, lng=lng, name=name,
                         foursqure_venue_id=foursqure_venue_id)


class Split(Attachment):
    """A split attachment (deprecated in the API).

    :param str token: the split token
    """

    def __init__(self, token):
        super().__init__(type='split', token=token)


class Emoji(Attachment):
    """An emoji attachment.

    :param str placeholder: the "stand-in" character for the emoji
    :param charmap: a list of 2-tuples specifying which emojis
    :type charmap: :class:`list`
    """

    def __init__(self, placeholder, charmap):
        super().__init__(type='emoji', placeholder=placeholder, charmap=charmap)


class Mentions(Attachment):
    """A mentions attachment.

    :param loci: the start and end indices of one or more mentions
    :type loci: :class:`list`
    :param user_ids: the user_ids of one or more users mentioned
    :type user_ids: :class:`list`
    """

    def __init__(self, loci, user_ids):
        super().__init__(type='mentions', loci=loci, user_ids=user_ids)


class Image(Attachment):
    """An image attachment.

    :param str url: the absolute URL for the image
    :param str source_url: an optional, absolute URL for the image source
    """

    def __init__(self, url, source_url=None):
        super().__init__(type='image', url=url, source_url=source_url)


# this is documented nowhere :(
class LinkedImage(Image):
    pass


class Images(base.Manager):
    """A manager for handling image uploads/downloads."""

    #: the base url for the pictures API
    base_url = 'https://image.groupme.com/'

    def from_file(self, fp):
        """Create a new image attachment from an image file.

        :param file fp: a file object containing binary image data
        :return: an image attachment
        :rtype: :class:`~groupy.api.attachments.Image`
        """
        image_urls = self.upload(fp)
        return Image(self, image_urls['url'])

    def upload(self, fp):
        """Upload image data to the image service.

        Call this, rather than :func:`from_file`, you don't want to
        create an attachment of the image.

        :param file fp: a file object containing binary image data
        :return: the URLs for the image uploaded
        :rtype: dict
        """
        url = utils.urljoin(self.url, 'pictures')
        response = self.session.post(url, files={'file': fp})
        image_urls = response.data['payload']
        return image_urls

    def download(self, image, url_field='url', suffix=None):
        """Download the binary data of an image attachment.

        :param image: an image attachment
        :type image: :class:`~groupy.api.attachments.Image`
        :param str url_field: the field of the image with the right URL
        :param str suffix: an optional URL suffix
        :return: binary image data
        :rtype: bytes
        """
        url = getattr(image, url_field)
        if suffix is not None:
            url = '.'.join(url, suffix)
        response = self.session.get(url)
        return response.content

    def download_preview(self, image, url_field='url'):
        """Downlaod the binary data of an image attachment at preview size.

        :param str url_field: the field of the image with the right URL
        :return: binary image data
        :rtype: bytes

        """
        return self.download(image, url_field=url_field, suffix='preview')

    def download_large(self, image, url_field='url'):
        """Downlaod the binary data of an image attachment at large size.

        :param str url_field: the field of the image with the right URL
        :return: binary image data
        :rtype: bytes

        """
        return self.download(image, url_field=url_field, suffix='large')

    def download_avatar(self, image, url_field='url'):
        """Downlaod the binary data of an image attachment at avatar size.

        :param str url_field: the field of the image with the right URL
        :return: binary image data
        :rtype: bytes

        """
        return self.download(image, url_field=url_field, suffix='avatar')
