==========
Change Log
==========

v0.7.0 (November 19, 2016)
==========================

- Fixed an issue with attachments not being serializable. Now an attempt to call their ``as_dict`` method is made (thank you to awctomlinson for pointing it out)
- Fixed problem with ``is_liked_by_me``, ``is_from_me`` and ``metions_me`` when used on ``DirectMessages`` (thank you to mmigrate)
- Added attachment support to ``Bot``'s ``post`` method (thank you again to mmigrate)
- Fixed a mispelling in the ``mentions_me`` method name (thank you adelq)

v0.6.6 (April 23, 2016)
=======================

- Fixed a typo in the docs regarding the type of the ``group`` parameter of the ``Bot`` class (kudos to JCDJulian)
- Fixed the ``Group.update`` method signature to include the ``group_id`` (kudos to mmirate)
- Fixed ``Member.identification`` such that it uses ``Member.guid`` rather than ``Member._guid`` (kudos to mmirate)
- Fixed the uncaught exception chain that occurred when a 304 was returned in ``Recipient.messages`` (thanks to dvmorris and sbonds for pointing it out)
- Updated the list of contributors

v0.6.5 (January 17, 2016)
=========================

- Fixed typo the ``Bot`` class that caused the bots to have a "gorup_id" (kudos to JCDJulian)
- All modules except ``object/listers.py`` and ``object/responses.py`` now have full test coverage
- Updated AUTHORS.rst with all contributors to date (feel free to PR with an email address added to your username)
- Fixed leftover markdown formatting in the CHANGELOG.rst file

v0.6.4 (December 31, 2015)
==========================

- Fixed bugs with creating bots (kudos to qlyoung)
- Fixed bugs with posting messages as bots (kudos again to qlyoung)
- Fixed typo bugs in ``Group`` class (kudos to t3zla)
- Fixed missing Python 3 trove classifier
- Added documentation for contributions
- Updated documentation for setup and installation
- Added a couple more unit tests
- Reconfigured tox test results to not clobber results from other environments

v0.6.3 (December 23, 2015)
==========================

- Added support for ``tox`` (envs py34,py35)
- Added support for ``bumpversion``
- Added ``make`` file for handy development
- Moved to ``nosetests`` and ``coverage``
- Split requirements into regular and testing
- Updated some of the installation/troubleshooting docs
- Merged in open pull-requests for various oversights (kudos to ScufyfNrdHrdr, rAntonioH, and JacobAMason)

v0.6.2 (May 3, 2015)
====================

- Fixed problem when posting messages as a bot
- Added ``refresh`` option for automatically updating group information after addition/removal of members
- Updated documentation

v0.6.1 (April 25, 2015)
=======================

- Fixed code in ``responses.py`` that was still using the old exception class name
- Changed the ``Member.remove()`` method to correctly use the ``id`` of the member rather than the ``user_id``
- Slight beefing up of some documentation

v0.5.8 (December 9, 2014)
=========================

- Fixed problems with ``requirements.txt`` and ``setup.py`` that caused problems installing from ``pip``
- Re-wrote many of the unittests (still in progress)
- Added Travis-CI and PyPI badges to the readme
- Bumped requirement for dropbox's ``responses`` to 0.3.0
- Now uses ``setup`` from ``setuptools`` rather than ``distutils.core``

v0.5.3 (September 19, 2014)
===========================

- Fix packaging bug that caused inner packages to not be installed via ``pip3``

v0.5.2 (September 14, 2014)
===========================

- Now installable via ``pip3``:

    .. code-block:: console

        $ pip3 install GroupyAPI


v0.5.1 (August 25, 2014)
========================

*Groups*

- Added a class method for creating a new group
- Added an instance method for destroying a group

*Members*

- Fixed member identification on dictionaries

*User*

- Fixed the enable/disable SMS methods (now class methods as they should be)

*Documentation*

- Added some module docstrings
- Added API docs for all attachment classes
- Added docs for split attachments
- Moved FilterList docs into the Advanced Usage section
- Rewrote API docs for enabling SMS mode
- Fixed bad sphinx references
- Fixed typos
- Added miscellaneous sections to the README
- Updated feature list

v0.5.0 (August 20, 2014)
========================

- Added support for downloaded the image of an image attachment
- Reorganized modules and project structure
- Updated documentation

v0.4.0 (August 18, 2014)
========================

- Added ability to list all known members
- Re-wrote attachments classes

v0.3.1 (August 14, 2014)
========================

- Fixed bug when adding members to a group
- Many additions to the documentation

v0.3.0 (August 12, 2014)
========================

- Added post and messages methods to members
- Added after_id parameter for direct messages
- Fixed liking and unliking direct messages
- Fixed listing former groups
- Fixed group lists being limited to a max of 500 items
- Documentation now available on `Read the Docs`_!

v0.2.0 (August 11, 2014)
========================

- Added MessagePager class for returning lists of messages

v0.1.3 (August 10, 2014)
========================

- Added attachment class
- Added basic documentation
- Fixed the automatic splitting of long texts
- Fixed invalid response error issue

v0.1.0 (August 9, 2014)
=======================

- Initial release

.. _Read the Docs: http://groupy.readthedocs.org/en/latest