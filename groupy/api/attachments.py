from . import base
from groupy import utils


class AttachmentMeta(type):
    _types = {}

    def __init__(cls, name, bases, attrs):
        cls._types[name.lower()] = cls


class Attachment(base.Resource, metaclass=AttachmentMeta):
    def __init__(self, type, **data):
        data['type'] = type
        self.data = data

    def to_json(self):
        return self.data

    @classmethod
    def from_data(cls, type, **data):
        try:
            return cls._types[type](**data)
        except KeyError:
            return cls(type=type, **data)

    @classmethod
    def from_bulk_data(cls, attachments):
        return [cls.from_data(**a) for a in attachments]


class Location(Attachment):
    def __init__(self, lat, lng, name):
        super().__init__(type='location', lat=lat, lng=lng, name=name)


class Split(Attachment):
    def __init__(self, token):
        super().__init__(type='split', token=token)


class Emoji(Attachment):
    def __init__(self, placeholder, charmap):
        super().__init__(type='emoji', placeholder=placeholder, charmap=charmap)


class Mentions(Attachment):
    def __init__(self, loci, user_ids):
        super().__init__(type='mentions', loci=loci, user_ids=user_ids)


class Image(Attachment):
    def __init__(self, url, source_url=None):
        super().__init__(type='image', url=url, source_url=source_url)


class LinkedImage(Image):
    pass


class Images(base.Manager):
    base_url = 'https://image.groupme.com/'

    def from_file(self, fp):
        image_urls = self.upload(fp)
        return Image(self, image_urls['url'])

    def upload(self, fp):
        url = utils.urljoin(self.url, 'pictures')
        response = self.session.post(url, files={'file': fp})
        image_urls = response.data['payload']
        return image_urls

    def download(self, image, url_field='url', suffix=None):
        url = getattr(image, url_field)
        if suffix is not None:
            url = '.'.join(url, suffix)
        response = self.session.get(url)
        return response.content

    def download_preview(self, image, url_field='url'):
        return self.download(image, url_field=url_field, suffix='preview')

    def download_large(self, image, url_field='url'):
        return self.download(image, url_field=url_field, suffix='large')

    def download_avatar(self, image, url_field='url'):
        return self.download(image, url_field=url_field, suffix='avatar')
