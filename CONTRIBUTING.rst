############################
Contributing to Django money
############################

Django-money is contribute-friendly project. Contributions are highly welcomed and appreciated.
There is a guideline for contributing.

Quickstart
----------

- All code contributions should be tested
- Code should conform to syntax conventions. There's a ``tox`` command to help fixing it: ``tox -e fix-lint``
- Documentation should be updated if it is required
- Put a note to the changelog.

Syntax and conventions
----------------------

The source code should conform to `PEP8`_ with following notice:

- Line length should not exceed **120** characters.

Running the tests
-----------------

We use ``tox`` to run the tests::

    $ tox -e lint,django111-py36,django111-py27

    The test environments above are usually enough to cover most cases locally.

.. _PEP8: http://www.python.org/dev/peps/pep-0008/

Report bugs
-----------

Report bugs in the `issue tracker <https://github.com/django-money/django-money/issues>`_.

If you are reporting a bug, please include:

* Any details about your local setup that might be helpful in troubleshooting,
  specifically the Python interpreter version, Django & django-money versions.
* Detailed steps to reproduce the bug.

If you can write a demonstration test that currently fails but should pass
(xfail), that is a very useful commit to make as well, even if you cannot
fix the bug itself.
