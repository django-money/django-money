Django-money
-----------

[![Travis](https://travis-ci.org/django-money/django-money.svg)](https://travis-ci.org/django-money/django-money)

A little Django app that uses `py-moneyed` to add support for Money fields in your models and forms.

Fork of the Django support that was in http://code.google.com/p/python-money/

This version adds tests, and comes with several critical bugfixes.

Django versions supported: 1.4.x, 1.5.x, 1.6.x, 1.7.x, 1.8.x

Python versions supported: 2.6.x, 2.7.x, pypy 2.1, 3.2.x\*, 3.3.x\*, 3.4.x\*
(* These versions of Python require py-moneyed 0.5 or higher )

Via `py-moneyed`, `django-money` gets:

 * Support for proper Money value handling (using the standard Money design pattern)
 * A currency class and definitions for all currencies in circulation
 * Formatting of most currencies with correct currency sign


Installation
------------

Django-money currently needs `py-moneyed` v0.4 (or later) to work.

You can obtain the source code for `django-money` from here:

    https://github.com/django-money/django-money

And the source for `py-moneyed` from here:

    https://github.com/limist/py-moneyed

Model usage
-----

Use as normal model fields

```python
    import moneyed
    from djmoney.models.fields import MoneyField
    from django.db import models

    class BankAccount(models.Model):

        balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
```


Searching for models with money fields:

```python
    from moneyed import Money, USD, CHF
    account = BankAccount(balance=Money(10, USD))
    swissAccount = BankAccount(balance=Money(10, CHF))

    account.save()
    swissAccount.save()

    BankAccount.objects.filter(balance__gt=Money(1, USD))
    # Returns the "account" object
```

If you use South to handle model migration, things will "Just Work" out of the box.
South is an optional dependency and things will work fine without it.

Adding a new Currency
---------------------

Currencies are listed on moneyed, and this modules use this to provide a choice
list on the admin, also for validation.

To add a new currency available on all the project, you can simple add this two
lines on your `settings.py` file

```python
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
        rounding_method=ROUND_HALF_EVEN)
```


To restrict the currencies listed on the project set a `CURRENCIES` variable with
a list of Currency codes on `settings.py`

```python
    CURRENCIES = ('USD', 'BOB')
```



**The list has to contain valid Currency codes**

Important note on model managers
--------------------------------

Django-money leaves you to use any custom model managers you like for your models, but it needs to
wrap some of the methods to allow searching for models with money values.

This is done automatically for the "objects" attribute in any model that uses MoneyField. However,
if you assign managers to some other attribute, you have to wrap your manager manually, like so:

```python
    from djmoney.models.managers import money_manager
    class BankAccount(models.Model):

        balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

        accounts = money_manager(MyCustomManager())
```

Also, the money_manager wrapper only wraps the standard QuerySet methods. If you define custom
QuerySet methods, that do not end up using any of the standard ones (like "get", "filter" and so on), then
you also need to manually decorate those custom methods, like so:

```python
    from djmoney.models.managers import understand_money

    class MyCustomQuerySet(QuerySet):

       @understand_money
       def my_custom_method(*args,**kwargs):
           # Awesome stuff
```

Format localization
--------------------------------

The formatting is turned on if you have set `USE_L10N = True` in the your settings file.

If formatting is disabled in the configuration, then in the templates will be used default formatting.

In the templates you can use a special tag to format the money.

In the file `settings.py` add to `INSTALLED_APPS` entry from the library `djmoney`:

```python
    INSTALLED_APPS += ( 'djmoney', )
```

In the template, add:

```
	{% load djmoney %}
	...
	{% money_localize money %}
```

and that is all.

Instructions to the tag `money_localize`:

```
        {% money_localize <money_object> [ on(default) | off ] [as var_name] %}
        {% money_localize <amount> <currency> [ on(default) | off ] [as var_name] %}
```

Examples:

The same effect:

```
        {% money_localize money_object %}
        {% money_localize money_object on %}
```

Assignment to a variable:

```
        {% money_localize money_object on as NEW_MONEY_OBJECT %}
```

Formatting the number with currency:

```
        {% money_localize '4.5' 'USD' %}
```

    Return::

        MoneyPatched object


Testing
--------------------------------

Install the required packages:

	git clone https://github.com/django-money/django-money

	cd ./django-money/

	pip install -e .[tests] # installation with required packages for testing

Recommended way to run the tests:

	tox

or

	python setup.py test


Testing the application in the current environment python:

 * the main tests

	./runtests.py

A handful of the tox environments are automatically tested on travis: see `gen_travis.bash` and `.travis.yml`.

Working with Exchange Rates
---------------------------

To work with exchange rates, check out this repo that builds off of django-money: https://github.com/evonove/django-money-rates
