"""
.. module:: config
   :platform: Unix, Windows
   :synopsis: Module containing configuration values.

.. moduleauthor:: Robert Grant <rhgrant10@gmail.com>

The ``config`` module contains all the configuration options.

"""

# Set this to the base URL for the GroupMe API (default is
# 'https://api.groupme.com/v3').
API_URL = 'https://api.groupme.com/v3'
"""The URL for the GroupMe API
"""

# Set this to the base URL for the GroupMe image service (default is
# 'https://image.groupme.com').
IMAGE_API_URL = 'https://image.groupme.com'
"""The URL for the GroupMe Image Service API
"""

# Set this to the location of the file containing your (default is
# '~/.groupy.key', which corresponds to '/home/<user>/.groupy.key' on Linux,
# and 'C:\Users\<user>\.groupy.key' on Windows).
KEY_LOCATION = '~/.groupy.key'
"""Full path to the file in which your access token can be found
"""
