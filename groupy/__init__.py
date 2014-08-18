"""The simple yet powerful wrapper for the GroupMe API.

.. module:: groupy
   :platform: Unix, Windows
   :synopsis: A wrapper for the GroupMe API

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

"""
import os
import warnings
import groupy.config


def _attempt_to_load_apikey():
    filepath = os.path.expanduser(groupy.config.KEY_LOCATION)
    try:
        with open(filepath, 'r') as f:
            groupy.config.API_KEY = f.read().strip()
    except IOError as e:
        groupy.config.API_KEY = None
        if e.errno != 2:
            warnings.warn(
                'key file {} exists but could not be opened: {}'.format(
                    groupy.config.KEY_LOCATION,
                    str(e)))    

_attempt_to_load_apikey()

from .objects import Group, User, Bot, Attachment, Member, FilterList
