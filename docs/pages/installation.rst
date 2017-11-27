============
Installation
============

To get started, you'll need to get an account at `Groupme.com <http://groupme.com>`_. Next, you'll need to obtain your access token so you can make API requests:

1. Login to the `developer portal`_.
2. Click the "Access Token" button on the top menu bar.
3. Your access token is displayed in bold text. Grab it.

Lastly, install Python >= 3.4. Now you're ready to install Groupy!


.. code-block:: console

    $ pip install GroupyAPI

.. _GroupMe account: http://groupme.com
.. _developer portal: https://dev.groupme.com/session/new


Troubleshooting
===============

Sometimes things go wrong. Here are some common things to check when
encountering problems after installing.


*It says no such package when I import groupy...*
    Check whether you copied the ``groupy`` package into the correct python package directory. It must be a directory on your ``sys.path``.

*I get an unauthorized error when I try to do anything...*
    Check that your API token is correct just before you use it to create a Groupy client.
