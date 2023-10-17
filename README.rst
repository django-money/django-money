django-money
============

.. image:: https://github.com/django-money/django-money/workflows/CI/badge.svg
   :target: https://github.com/django-money/django-money/actions
   :alt: Build Status

.. image:: http://codecov.io/github/django-money/django-money/coverage.svg?branch=main
   :target: http://codecov.io/github/django-money/django-money?branch=main
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-money/badge/?version=latest
   :target: http://django-money.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/django-money.svg
   :target: https://pypi.python.org/pypi/django-money
   :alt: PyPI

A little Django app that uses `py-moneyed <https://github.com/py-moneyed/py-moneyed>`__ to add support for Money
fields in your models and forms.

* Django versions supported: 2.2, 3.2, 4.0, 4.1, 4.2
* Python versions supported: 3.7, 3.8, 3.9, 3.10, 3.11
* PyPy versions supported: PyPy3 (for Django <= 4.0)

If you need support for older versions of Django and Python, please refer to older releases mentioned in `the release notes <https://django-money.readthedocs.io/en/latest/changes.html>`__.

Through the dependency `py-moneyed <https://github.com/py-moneyed/py-moneyed>`__, ``django-money`` gets:

* Support for proper Money value handling (using the standard Money
  design pattern)
* A currency class and definitions for all currencies in circulation
* Formatting of most currencies with correct currency sign

Installation
------------

Using `pip`:

.. code:: bash

   $ pip install django-money

This automatically installs ``py-moneyed`` v1.2 (or later).

Add ``djmoney`` to your ``INSTALLED_APPS``. This is required so that money field are displayed correctly in the admin.

.. code:: python

   INSTALLED_APPS = [
      ...,
      'djmoney',
      ...
   ]

Model usage
-----------

Use as normal model fields:

.. code:: python

        from djmoney.models.fields import MoneyField
        from django.db import models


        class BankAccount(models.Model):
            balance = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

To comply with certain strict accounting or financial regulations, you may consider using ``max_digits=19`` and ``decimal_places=4``, see more in this `StackOverflow answer <https://stackoverflow.com/a/224866/405682>`__

It is also possible to have a nullable ``MoneyField``:

.. code:: python

        class BankAccount(models.Model):
            money = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency=None)

        account = BankAccount.objects.create()
        assert account.money is None
        assert account.money_currency is None

Searching for models with money fields:

.. code:: python

        from djmoney.money import Money


        account = BankAccount.objects.create(balance=Money(10, 'USD'))
        swissAccount = BankAccount.objects.create(balance=Money(10, 'CHF'))

        BankAccount.objects.filter(balance__gt=Money(1, 'USD'))
        # Returns the "account" object

The default currency code length is `3` but you can change it with the `CURRENCY_CODE_MAX_LENGTH` setting.

Caution: this setting also affects the initial migration of the `exchange` plugin, so changing it after running
the initial migration has no effect. (You'd need to `manage migrate exchange zero` and migrate again if you want
to change it).

Field validation
----------------

There are 3 different possibilities for field validation:

* by numeric part of money despite on currency;
* by single money amount;
* by multiple money amounts.

All of them could be used in a combination as is shown below:

.. code:: python

        from django.db import models
        from djmoney.models.fields import MoneyField
        from djmoney.money import Money
        from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator


        class BankAccount(models.Model):
            balance = MoneyField(
                max_digits=10,
                decimal_places=2,
                validators=[
                    MinMoneyValidator(10),
                    MaxMoneyValidator(1500),
                    MinMoneyValidator(Money(500, 'NOK')),
                    MaxMoneyValidator(Money(900, 'NOK')),
                    MinMoneyValidator({'EUR': 100, 'USD': 50}),
                    MaxMoneyValidator({'EUR': 1000, 'USD': 500}),
                ]
            )

The ``balance`` field from the model above has the following validation:

* All input values should be between 10 and 1500 despite on currency;
* Norwegian Crowns amount (NOK) should be between 500 and 900;
* Euros should be between 100 and 1000;
* US Dollars should be between 50 and 500;

Adding a new Currency
---------------------

Currencies are listed on moneyed, and this modules use this to provide a
choice list on the admin, also for validation.

To add a new currency available on all the project, you can simply add
these few lines to your ``settings.py`` file:

.. code:: python

        import moneyed

        BOB = moneyed.add_currency(
            code='BOB',
            numeric='068',
            name='Peso boliviano',
            countries=('BOLIVIA', )
        )


To restrict the currencies listed on the project set a ``CURRENCIES``
variable with a list of Currency codes on ``settings.py``

.. code:: python

        CURRENCIES = ('USD', 'BOB')

**The list has to contain valid Currency codes**

Additionally there is an ability to specify currency choices directly:

.. code:: python

        CURRENCIES = ('USD', 'EUR')
        CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €')]

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


Note on serialization
---------------------

Django-money provides a custom deserializer, it is not registered
by default so you will have to actively register it in your ``settings.py``.

.. code:: python

    SERIALIZATION_MODULES = {"json": "djmoney.serializers"}


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

        Money object


Testing
-------

Install the required packages:

::

    git clone https://github.com/django-money/django-money

    cd ./django-money/

    pip install -e ".[test]" # installation with required packages for testing

Recommended way to run the tests:

.. code:: bash

    tox

Testing the application in the current environment python:

.. code:: bash

    make test

Working with Exchange Rates
---------------------------

To work with exchange rates, add the following to your ``INSTALLED_APPS``.

.. code:: python

    INSTALLED_APPS = [
        ...,
        'djmoney.contrib.exchange',
    ]

Also, it is required to have ``certifi`` installed.
It could be done via installing ``djmoney`` with ``exchange`` extra:

.. code:: bash

    pip install "django-money[exchange]"

To create required relations run ``python manage.py migrate``. To fill these relations with data you need to choose a
data source. Currently, 2 data sources are supported - https://openexchangerates.org/ (default) and https://fixer.io/.
To choose another data source set ``EXCHANGE_BACKEND`` settings with importable string to the backend you need:

.. code:: python

    EXCHANGE_BACKEND = 'djmoney.contrib.exchange.backends.FixerBackend'

If you want to implement your own backend, you need to extend ``djmoney.contrib.exchange.backends.base.BaseExchangeBackend``.
Two data sources mentioned above are not open, so you have to specify access keys in order to use them:

``OPEN_EXCHANGE_RATES_APP_ID`` - '<your actual key from openexchangerates.org>'

``FIXER_ACCESS_KEY`` - '<your actual key from fixer.io>'

Backends return rates for a base currency, by default it is USD, but could be changed via ``BASE_CURRENCY`` setting.
Open Exchanger Rates & Fixer supports some extra stuff, like historical data or restricting currencies
in responses to the certain list. In order to use these features you could change default URLs for these backends:

.. code:: python

    OPEN_EXCHANGE_RATES_URL = 'https://openexchangerates.org/api/historical/2017-01-01.json?symbols=EUR,NOK,SEK,CZK'
    FIXER_URL = 'http://data.fixer.io/api/2013-12-24?symbols=EUR,NOK,SEK,CZK'

Or, you could pass it directly to ``update_rates`` method:

.. code:: python

    >>> from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend
    >>> backend = OpenExchangeRatesBackend(url='https://openexchangerates.org/api/historical/2017-01-01.json')
    >>> backend.update_rates(symbols='EUR,NOK,SEK,CZK')

There is a possibility to use multiple backends in the same time:

.. code:: python

    >>> from djmoney.contrib.exchange.backends import FixerBackend, OpenExchangeRatesBackend
    >>> from djmoney.contrib.exchange.models import get_rate
    >>> OpenExchangeRatesBackend().update_rates()
    >>> FixerBackend().update_rates()
    >>> get_rate('USD', 'EUR', backend=OpenExchangeRatesBackend.name)
    >>> get_rate('USD', 'EUR', backend=FixerBackend.name)

Regular operations with ``Money`` will use ``EXCHANGE_BACKEND`` backend to get the rates.
Also, there are two management commands for updating rates and removing them:

.. code:: bash

    $ python manage.py update_rates
    Successfully updated rates from openexchangerates.org
    $ python manage.py clear_rates
    Successfully cleared rates for openexchangerates.org

Both of them accept ``-b/--backend`` option, that will update/clear data only for this backend.
And ``clear_rates`` accepts ``-a/--all`` option, that will clear data for all backends.

To set up a periodic rates update you could use Celery task:

.. code:: python

    CELERYBEAT_SCHEDULE = {
        'update_rates': {
            'task': 'path.to.your.task',
            'schedule': crontab(minute=0, hour=0),
            'kwargs': {}  # For custom arguments
        }
    }

Example task implementation:

.. code:: python

    from django.utils.module_loading import import_string

    from celery import Celery
    from djmoney import settings


    app = Celery('tasks', broker='pyamqp://guest@localhost//')


    @app.task
    def update_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
        backend = import_string(backend)()
        backend.update_rates(**kwargs)

To convert one currency to another:

.. code:: python

    >>> from djmoney.money import Money
    >>> from djmoney.contrib.exchange.models import convert_money
    >>> convert_money(Money(100, 'EUR'), 'USD')
    <Money: 122.8184375038380800 USD>

Exchange rates are integrated with Django Admin.

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

Make sure that ``djmoney`` and is in the ``INSTALLED_APPS`` of your
``settings.py`` and that ``rest_framework`` has been installed. MoneyField will
automatically register a serializer for Django REST Framework through
``djmoney.apps.MoneyConfig.ready()``.

You can add a serializable field the following way:

.. code:: python

    from djmoney.contrib.django_rest_framework import MoneyField

    class Serializers(serializers.Serializer):
        my_computed_prop = MoneyField(max_digits=10, decimal_places=2)


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

Note that when specifying individual fields on your serializer, the amount and currency fields are treated separately.
To achieve the same behaviour as above you would include both field names:

.. code:: python

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Expenses
            fields = ('id', 'amount', 'amount_currency')

Customization
-------------

If there is a need to customize the process deconstructing ``Money`` instances onto Django Fields and the other way around,
then it is possible to use a custom descriptor like this one:

.. code:: python

    class MyMoneyDescriptor:

        def __get__(self, obj, type=None):
            amount = obj.__dict__[self.field.name]
            return Money(amount, "EUR")

It will always use ``EUR`` for all ``Money`` instances when ``obj.money`` is called. Then it should be passed to ``MoneyField``:

.. code:: python

    class Expenses(models.Model):
        amount = MoneyField(max_digits=10, decimal_places=2, money_descriptor_class=MyMoneyDescriptor)


Background
----------

This project is a fork of the Django support that was in
http://code.google.com/p/python-money/

This version adds tests, and comes with several critical bugfixes.
