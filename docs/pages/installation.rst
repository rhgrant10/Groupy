============
Installation
============

Prerequisites
=============

To get started, you'll need to get an account at `Groupme.com <http://groupme.com>`_. Next, you'll need to obtain your access token so you can make API requests:

1. Login to the `developer portal`_.
2. Click the "Access Token" button on the top menu bar.
3. Your access token is displayed in bold text. Grab it.

Lastly, install Python >= 3.4. Now you're ready to install Groupy!

.. _GroupMe account: http://groupme.com
.. _developer portal: https://dev.groupme.com/session/new

Instructions
============

Below are instructions for installing for either use or development.

Typical
-------

.. code-block:: console

    $ pip install GroupyAPI


Development
-----------

Clone the repository:

.. code-block:: console

    $ git clone git clone https://github.com/rhgrant10/Groupy.git
    $ cd Groupy

See how the existing tests are doing:

.. code-block:: console

    $ tox

Probably easier to work on it within a virtual environment:

.. code-block:: console

    $ python3 -m venv env
    $ souce env/bin/activate
    $ pip install -r requirements.txt && pip install -r testing_requirements.txt
    $ pip install -e .
    $ ipython
    Python 3.6.1 (default, Apr  4 2017, 09:40:21)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: import groupy

    In [2]: 

.. note:: You do *not* need an API token to run tests.

Troubleshooting
===============

Sometimes things go wrong. Here are some common things to check when
encountering problems after installing.


*It says no such package when I import groupy...*
    Check whether you copied the ``groupy`` package into the correct python package directory. It must be a directory on your ``sys.path``.

*I get an unauthorized error when I try to do anything...*
    Check that your API token is correct just before you use it to create a Groupy client.
