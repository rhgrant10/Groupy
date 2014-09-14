from distutils.core import setup
setup(
    name = 'GroupyAPI',
    packages = ['groupy'], # this must be the same as the name above
    version = '0.5.2',
    description = 'The simple yet powerful wrapper for the GroupMe API',
    author = 'Robert Grant',
    author_email = 'rhgrant10@gmail.com',
    url = 'https://github.com/rhgrant10/Groupy', # use the URL to the github repo
    keywords = ['api', 'GroupMe'], # arbitrary keywords
    classifiers = [],
    long_description=open('README.rst', 'r').read()
)
