#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

with open('testing_requirements.txt') as test_requirements_file:
    test_requirements = test_requirements_file.read().splitlines()


setup(
    name='GroupyAPI',
    version='0.7.0',
    description='The simple yet powerful wrapper for the GroupMe API',
    long_description=readme + '\n\n' + changelog,
    author='Robert Grant',
    author_email='rhgrant10@gmail.com',
    url='https://github.com/rhgrant10/Groupy',
    packages=[
        'groupy', 'groupy.object', 'groupy.api'
    ],
    package_dir={'groupy':
                 'groupy'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License, Version 2.0",
    keywords=['api', 'GroupMe'],
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Chat',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
