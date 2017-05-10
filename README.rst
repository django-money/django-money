Django-money
============

.. image:: https://travis-ci.org/django-money/django-money.svg?branch=master
   :target: https://travis-ci.org/django-money/django-money
   :alt: Build Status

.. image:: http://codecov.io/github/django-money/django-money/coverage.svg?branch=master
   :target: http://codecov.io/github/django-money/django-money?branch=master
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-money/badge/?version=latest
   :target: http://django-money.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/django-money.svg
   :target: https://pypi.python.org/pypi/django-money
   :alt: PyPI

A little Django app that uses ``py-moneyed`` to add support for Money
fields in your models and forms.

Fork of the Django support that was in
http://code.google.com/p/python-money/

This version adds tests, and comes with several critical bugfixes.

Django versions supported: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11

Python versions supported: 2.6, 2.7, 3.2, 3.3, 3.4, 3.5, 3.6

PyPy versions supported: PyPy 2.6, PyPy3 2.4

Via ``py-moneyed``, ``django-money`` gets:

-  Support for proper Money value handling (using the standard Money
   design pattern)
-  A currency class and definitions for all currencies in circulation
-  Formatting of most currencies with correct currency sign

Installation
------------

Django-money currently needs ``py-moneyed`` v0.7 (or later) to work.

You can obtain the source code for ``django-money`` from here:

::

    https://github.com/django-money/django-money

And the source for ``py-moneyed`` from here:

::

    https://github.com/limist/py-moneyed

Using `pip`:

    pip install py-moneyed django-money

Model usage
-----------

Use as normal model fields

.. code:: python

        import moneyed
        from djmoney.models.fields import MoneyField
        from django.db import models


        class BankAccount(models.Model):
            balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

Searching for models with money fields:

.. code:: python

        from moneyed import Money, USD, CHF


        account = BankAccount.objects.create(balance=Money(10, USD))
        swissAccount = BankAccount.objects.create(balance=Money(10, CHF))

        BankAccount.objects.filter(balance__gt=Money(1, USD))
        # Returns the "account" object

Special note on serialized arguments: if your model definition
requires serializing an instance of ``Money``, you can use ``MoneyPatched``
instead.

.. code:: python

        from django.core.validators import MinValueValidator
        from django.db import models
        from djmoney.models.fields import MoneyField, MoneyPatched


        class BankAccount(models.Model):
            balance = MoneyField(max_digits=10, decimal_places=2, validators=[MinValueValidator(MoneyPatched(100, 'GBP'))])


If you use South to handle model migration, things will "Just Work" out
of the box. South is an optional dependency and things will work fine
without it.

Adding a new Currency
---------------------

Currencies are listed on moneyed, and this modules use this to provide a
choice list on the admin, also for validation.

To add a new currency available on all the project, you can simple add
this two lines on your ``settings.py`` file

.. code:: python

        import moneyed
        from moneyed.localization import _FORMATTER
        from decimal import ROUND_HALF_EVEN


        BOB = moneyed.add_currency(
            code='BOB',
            numeric='068',
            name='Peso boliviano',
            countries=('BOLIVIA', )
        )

        # Currency Formatter will output 2.000,00 Bs.
        _FORMATTER.add_sign_definition(
            'default',
            BOB,
            prefix=u'Bs. '
        )

        _FORMATTER.add_formatting_definition(
            'es_BO',
            group_size=3, group_separator=".", decimal_point=",",
            positive_sign="",  trailing_positive_sign="",
            negative_sign="-", trailing_negative_sign="",
            rounding_method=ROUND_HALF_EVEN
        )

To restrict the currencies listed on the project set a ``CURRENCIES``
variable with a list of Currency codes on ``settings.py``

.. code:: python

        CURRENCIES = ('USD', 'BOB')

**The list has to contain valid Currency codes**

Additionally there is an ability to specify currency choices directly:

.. code:: python

        CURRENCIES = ('USD', 'EUR')
        CURRENCY_CHOICES = (('USD', 'USD $'), ('EUR', 'EUR €'))

Important note on model managers
--------------------------------

Django-money leaves you to use any custom model managers you like for
your models, but it needs to wrap some of the methods to allow searching
for models with money values.

This is done automatically for the "objects" attribute in any model that
uses MoneyField. However, if you assign managers to some other
attribute, you have to wrap your manager manually, like so:

.. code:: python

        from djmoney.models.managers import money_manager


        class BankAccount(models.Model):
            balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
            accounts = money_manager(MyCustomManager())

Also, the money\_manager wrapper only wraps the standard QuerySet
methods. If you define custom QuerySet methods, that do not end up using
any of the standard ones (like "get", "filter" and so on), then you also
need to manually decorate those custom methods, like so:

.. code:: python

        from djmoney.models.managers import understands_money


        class MyCustomQuerySet(QuerySet):

           @understands_money
           def my_custom_method(*args, **kwargs):
               # Awesome stuff

Format localization
-------------------

The formatting is turned on if you have set ``USE_L10N = True`` in the
your settings file.

If formatting is disabled in the configuration, then in the templates
will be used default formatting.

In the templates you can use a special tag to format the money.

In the file ``settings.py`` add to ``INSTALLED_APPS`` entry from the
library ``djmoney``:

.. code:: python

        INSTALLED_APPS += ('djmoney', )

In the template, add:

::

        {% load djmoney %}
        ...
        {% money_localize money %}

and that is all.

Instructions to the tag ``money_localize``:

::

            {% money_localize <money_object> [ on(default) | off ] [as var_name] %}
            {% money_localize <amount> <currency> [ on(default) | off ] [as var_name] %}

Examples:

The same effect:

::

            {% money_localize money_object %}
            {% money_localize money_object on %}

Assignment to a variable:

::

            {% money_localize money_object on as NEW_MONEY_OBJECT %}

Formatting the number with currency:

::

            {% money_localize '4.5' 'USD' %}

::

    Return::

        MoneyPatched object

Admin integration
-----------------

For Django **1.7+** integration works automatically if ``djmoney`` is in the ``INSTALLED_APPS``.

For older versions you should use the following code:

.. code:: python

    from djmoney.admin import setup_admin_integration
    
    # NOTE. Only for Django < 1.7
    setup_admin_integration()


There is no single opinion about where to place on-start-up code in Django < 1.7, but we'd recommend to place it
in the top-level `urls.py`.

Testing
-------

Install the required packages:

::

    git clone https://github.com/django-money/django-money

    cd ./django-money/

    pip install -e .[tests] # installation with required packages for testing

Recommended way to run the tests:

.. code:: bash

    tox

Testing the application in the current environment python:

.. code:: bash

    make test

Working with Exchange Rates
---------------------------

To work with exchange rates, check out this repo that builds off of
django-money: https://github.com/evonove/django-money-rates

django-money can be configured to automatically use this app for currency
conversions by settings ``AUTO_CONVERT_MONEY = True`` in your Django
settings. Note that currency conversion is a lossy process, so automatic
conversion is usually a good strategy only for very simple use cases. For most
use cases you will need to be clear about exactly when currency conversion
occurs, and automatic conversion can hide bugs. Also, with automatic conversion
you lose some properties like commutativity (``A + B == B + A``) due to
conversions happening in different directions.

Usage with Django REST Framework
--------------------------------

In Django **1.7+**, for MoneyFields to automatically work with Django REST Framework, make sure
that ``djmoney`` is in the ``INSTALLED_APPS`` of your ``settings.py``.

For older versions you should use the following code:

.. code:: python

    from djmoney.contrib.django_rest_framework import register_money_field
 
    # NOTE. Only for Django < 1.7
    register_money_field()

Just put it in the end of your root ``urls.py`` file.

Built-in serializer works in the following way:

.. code:: python

    class Expenses(models.Model):
        amount = MoneyField(max_digits=10, decimal_places=2)


    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Expenses
            fields = '__all__'

    >>> instance = Expenses.objects.create(amount=Money(10, 'EUR'))
    >>> serializer = Serializer(instance=instance)
    >>> serializer.data
    ReturnDict([
        ('id', 1),
        ('amount_currency', 'EUR'),
        ('amount', '10.000'),
    ])

Known Issues
------------
Updates to a model form will not save in Django 1.10.1.  They will save in 1.10.0 and is expected to be fixed in Django 1.10.2.
::

     https://github.com/django/django/pull/7217
