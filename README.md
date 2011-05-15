Django-money
-----------

A little django app that uses py-moneyed to add support for Money fields in your models and forms. 

Fork of the django support that was in http://code.google.com/p/python-money/

Via py-moneyed, django-moneyed gets:

 * Support for proper Money value handling (using the standard Money design pattern)
 * A currency class and definitions for all currencies in circulation
 * Formatting of most currencies with correct currency sign


Installation
------------

Django-money currently needs a special version of py-moneyed to work (2011-05-15). This will be resolved as soon as 
the fork is merged into py-moneyed main branch.

Until then, install py-moneyed from here:

    git clone https://jakewins@github.com/jakewins/py-moneyed.git
    cd py-moneyed
    python setup.py install

And then, install py-moneyed like so:

    git clone https://jakewins@github.com/jakewins/django-money.git
    cd django-money
    python setup.py install
