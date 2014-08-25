============
Installation
============

Prerequisites
=============

To get started, you'll need to *get an account* at
`Groupme.com <http://groupme.com>`_.

Got it? Great!

Now you'll need to *obtain your access token* so you can make API requests:

1. Login to the `developer portal`_.
2. Click the "Bots" button on the top menu bar.
3. Click the "Click here to reveal" button.
4. Copy your access token.

You must also *create a key file*.

1. Paste your access token into a new file.
2. Save it as ``.groupy.key`` in your user's home directory.

Lastly, ensure you're running Python >= 3! Now you're ready to install Groupy! 

.. _GroupMe account: http://groupme.com
.. _developer portal: https://dev.groupme.com/session/new

Installing
==========

Below are instructions for various ways of installating.

Using ``pip``
-------------

.. note::

	Installation via ``pip`` coming soon!

From Source
-----------

Basic Steps
^^^^^^^^^^^

1) Download `Groupy from GitHub`_. 
2) Copy the ``groupy`` directory (``Groupy/groupy``) into your package directory
   for ``Python3``. 

.. note:: 

	Your package directory may be elsewhere. For help determining the correct
	location, see `this StackOverflow question`_.

With ``git``
^^^^^^^^^^^^

If you have ``git``, it's as easy as: 

.. code-block:: console

    $ git clone https://github.com/rhgrant10/Groupy.git
    $ cd Groupy
    $ cp -r groupy /usr/lib/python3/dist-packages	# see note above


Without ``git``
^^^^^^^^^^^^^^^

If you don't have ``git`` installed, ask yourself `why`_?

If you're satisfied with your answer to that question and you're still reading
this section, fine. You don't *need* ``git``. You can download it as a ZIP file.

- `master branch`_
- `dev branch`_

Installation is a simple matter of unzipping the file and copying over the
``groupy`` directory to your ``Python3`` package directory.

.. code-block:: console

	$ wget https://github.com/rhgrant10/Groupy/archive/master.zip
	$ unzip master.zip
	$ cd Groupy-master
	$ cp -r groupy /usr/lib/python3/dist-packages	# see note above

.. _Groupy from GitHub: http://github.com/rhgrant10/Groupy
.. _why: http://git-scm.com/downloads
.. _master branch: https://github.com/rhgrant10/Groupy/archive/master.zip
.. _dev branch: https://github.com/rhgrant10/Groupy/archive/dev.zip
.. _this StackOverflow question: http://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory

Troubleshooting
===============

Sometimes things go wrong. Here are some common things to check when
encountering problems after installing.

*It says no such package when I import groupy...*

    Check whether you copied the ``groupy`` package into the correct python
    pacakge directory. It must be a directory on your ``sys.path``.

*I get an unauthorized error when I try to do anything...*

    Check whether your key file (``.groupy.key`` by default) contains your API
    token, and that ``groupy/config.py`` contains a definition for
    ``KEY_LOCATION`` that correctly specifies the location and name of your key
    file.
