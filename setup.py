from setuptools import setup

setup(
    name='GroupyAPI',
    packages=['groupy', 'groupy.object', 'groupy.api'],
    version='0.6.1',
    install_requires=[
        "responses==0.3.0",
        "requests==2.3.0",
        "Pillow==2.5.3",
    ],
    description='The simple yet powerful wrapper for the GroupMe API',
    author='Robert Grant',
    author_email='rhgrant10@gmail.com',
    url='https://github.com/rhgrant10/Groupy', # use the URL to the github repo
    keywords=['api', 'GroupMe'], # arbitrary keywords
    classifiers=['Programming Language :: Python :: 3'],
    long_description=open('README.rst', 'r').read()
)
