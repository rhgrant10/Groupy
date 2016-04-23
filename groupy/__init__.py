"""The simple yet powerful wrapper for the GroupMe API.

.. module:: groupy
   :platform: Unix, Windows
   :synopsis: A wrapper for the GroupMe API

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
import os
import warnings

from . import config
from .object.responses import Group, User, Bot, Member
from .object.listers import FilterList
from .object import attachments

__author__ = 'Robert Grant'
__email__ = 'rhgrant10@gmail.com'
__version__ = '0.6.6'


def _attempt_to_load_apikey():
    filepath = os.path.expanduser(config.KEY_LOCATION)
    try:
        with open(filepath, 'r') as f:
            config.API_KEY = f.read().strip()
    except IOError as e:
        config.API_KEY = None
        if e.errno != 2:
            warnings.warn(
                'key file {} exists but could not be opened: {}'.format(
                    config.KEY_LOCATION,
                    str(e)))

_attempt_to_load_apikey()
