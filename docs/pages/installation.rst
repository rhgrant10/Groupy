============
Installation
============

You'll need to `get a GroupMe account`_ to get started. Got it? Okay, now
you'll need to obtain your access token so you can make API requests:

1) Login to the `developer portal`_.
2) Click the "Bots" button on the top menu bar.
3) Click the "Click here to reveal" button and copy your access token.
4) Paste it into a new file called ``.groupy.key`` and save it in your user's
   home directory.

.. _get a GroupMe account: http://groupme.com
.. _developer portal: https://dev.groupme.com/session/new

Now you're ready to install Groupy! 

Using ``pip``
-------------

.. note::

	Installation via ``pip`` coming soon!

From Source
-----------

1) Download `Groupy from GitHub`_. 
2) Copy the package directory (``Groupy/groupy``) into your package directory
   for ``Python3``. 

.. _Groupy from GitHub: http://github.com/rhgrant10/Groupy

If you have ``git``, it's as easy as: 

   .. code-block:: bash

       $ git clone https://github.com/rhgrant10/Groupy.git
       $ cd Groupy
       $ cp -r groupy /usr/lib/python3/dist-packages	# see note below

If you don't have ``git`` installed (and don't wish to install it), that's okay
too! You can get the project as a zip file using ``wget``:

.. code-block:: console

	   $ wget https://github.com/rhgrant10/Groupy/archive/master.zip
	   $ unzip master.zip
	   $ cd Groupy-master
	   $ cp -r groupy /usr/lib/python3/dist-packages	# see note below

If neither ``git`` nor ``wget`` are on your system (for example, you might have
Windows installed rather than a flavor of Linux), that's still okay! Simply
click this `link to download it using your browser`_ as a zip file.

.. _link to download it using your browser: https://github.com/rhgrant10/Groupy/archive/master.zip

.. note:: 

	See `this StackOverflow question`_ for help determining the right location.

.. _this StackOverflow question: http://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory

There, all done! Feels good, right? 

Verifying Installation
----------------------

You can verify that the installation worked by simply importing ``groupy`` from
a ``Python3`` shell:

.. code-block::

	$ python3
	Python 3.4.1 (default, Aug 11 2014, 10:05:47) 
	[GCC 4.8.2] on linux
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import groupy
	>>> 

If you get no errors, you're good to go! 

