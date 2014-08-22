"""
.. module:: attachments
    :platform: Unix, Windows
    :synopsis: A module containing all attachment classes

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

This module contains classes for the different types of attachments.

"""

from ..api import endpoint

import json

class Attachment:
    def __init__(self, type):
        self.type = type
        
    def as_dict(self):
        return self.__dict__
        

class GenericAttachment(Attachment):
    def __init__(self, type, **kwargs):
        super().__init__(type)
        for k in kwargs:
            setattr(self, k, kwargs[k])


class Image(Attachment):
    def __init__(self, url, source_url=None):
        super().__init__('image')
        self.url = url
        self.source_url = source_url
        
    def __repr__(self):
        return "Image(url={!r})".format(self.url)
        
    @classmethod
    def file(cls, image):
        return cls(endpoint.Images.create(image)['url'])
        
    def download(self):
        return endpoint.Images.download(self.url)


class Location(Attachment):
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
    def __init__(self, placeholder, charmap):
        super().__init__('emoji')
        self.placeholder = placeholder
        self.charmap = charmap
        
    def __repr__(self):
        return "Emoji(placeholder={!r}, charmap={!r})".format(
            self.placeholder, self.charmap)


class Split(Attachment):
    def __init__(self, token):
        super().__init__('split')
        self.token = token

    def __repr__(self):
        return "Split(token={!r})".format(self.token)


class Mentions(Attachment):
    def __init__(self, user_ids, loci=None):
        super().__init__('mentions')
        self.loci = loci
        self.user_ids = user_ids

    def __repr__(self):
        return "Mentions({!r})".format(self.user_ids)


class AttachmentFactory:
    _factories = {
        'image': Image,
        'location': Location,
        'emoji': Emoji,
        'mentions': Mentions,
        'split': Split
    }

    @classmethod
    def create(cls, **kwargs):
        t = kwargs.pop('type', None)
        try:
            return cls._factories[t](**kwargs)
        except TypeError:
            print('type: {}'.format(t))
            print(json.dumps(kwargs, indent=2))
        except KeyError:
            return GenericAttachment(t, **kwargs)        
        

