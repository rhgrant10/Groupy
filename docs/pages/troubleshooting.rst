===============
Troubleshooting
===============


Sometimes things go wrong. Here are some common things to check when
encountering problems after installing.


*It says no such package when I import groupy...*
    Check whether you copied the ``groupy`` package into the correct python package directory. It must be a directory on your ``sys.path``.

*I get an unauthorized error when I try to do anything...*
    Check that your API token is correct just before you use it to create a Groupy client.

*I get an HTTP 429 response when I try to send a direct message to another user...*
    You must use an API access token obtained via creation of an `application`_.

.. _application: https://dev.groupme.com/applications
