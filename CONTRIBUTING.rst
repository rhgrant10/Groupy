.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/rhgrant10/Groupy/issues.

If you are reporting a bug, please include:

* Your python version
* Your groupy version
* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Groupy could always use more documentation, whether as part of the
official Groupy docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/rhgrant10/Groupy/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `Groupy` for local development.

1. Fork the `Groupy repo on GitHub <https://github.com/rhgrant10/Groupy>`_.
2. Clone your fork locally::

    $ git clone git@github.com:YOUR_NAME_HERE/Groupy.git

3. Install your local copy into a virtualenv. Since 3.3, Python ships with its own virutal environment creator: `venv`. Usage is simple::

    $ cd Groupy/
    $ pyvenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt && pip install testing_requirements.txt

4. Create a branch *from the dev branch* for local development::

    $ git checkout -b name-of-your-bugfix-or-feature dev

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8, have great coverage, and pass all tests on all supported versions of python. Sounds tough, but `tox` makes this easy::

    $ tox

Note that if you update ``requirements.txt`` or ``testing_requirements.txt`` you must tell tox to recreate its virtual environments using the ``-r`` flag::

    $ tox -r

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit
    $ git push origin name-of-your-bugfix-or-feature

Please make sure to:

- *not* to commit sensitive data or extra files. You can use ``git add -p`` to add parts of files if necessary.
- follow `proper git commit message standards <http://chris.beams.io/posts/git-commit/>`_. In particular, the first line should be under 60 characters long, and any detail should begin on the 3rd line (the second line must be blank).

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include **tests**.
2. If the pull request adds functionality, the **docs** should be updated. Put
   your new functionality into a function with a **docstring**, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.4 and 3.5. Check
   https://travis-ci.org/rhgrant10/Groupy/pull_requests
   and make sure that the tests pass for all supported Python versions.

