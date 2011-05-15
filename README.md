Django-money
-----------

A little django app that uses py-moneyed to add support for Money fields in your models and forms. 

Fork of the django support that was in http://code.google.com/p/python-money/

This version adds tests, and comes with several critical bugfixes. 

Via py-moneyed, django-moneyed gets:

 * Support for proper Money value handling (using the standard Money design pattern)
 * A currency class and definitions for all currencies in circulation
 * Formatting of most currencies with correct currency sign


Installation
------------

Django-money currently needs a special version of py-moneyed to work (2011-05-15). This will be resolved as soon as 
my fork of it is approved and merged into py-moneyed main branch.

Until then, install py-moneyed from here:

    git clone https://jakewins@github.com/jakewins/py-moneyed.git
    cd py-moneyed
    python setup.py install

And then, install py-moneyed like so:

    git clone https://jakewins@github.com/jakewins/django-money.git
    cd django-money
    python setup.py install

Model usage
-----

Use as normal model fields

    import moneyed
    from djmoney.models.fields import MoneyField
    from django.db import models
    
    class BankAccount(models.Model):
        
        balance = MoneyField(max_digits=10, decimal_places=2, default_currency=moneyed.USD)


Searching for models with money fields:

    from moneyed import Money, USD, CHF
    account = BankAccount(balance=Money(10, USD))
    swissAccount = BankAccount(balance=Money(10, CHF))

    account.save()
    swissAccount.save()

    BankAccount.objects.filter(balance__gt=Money(1, USD))
    # Returns the "account" object

Important note on model managers
--------------------------------

Django-money leaves you to use any custom model managers you like for your models, but it needs to
wrap some of the methods to allow searching for models with money values.

This is done automatically for the "objects" attribute in any model that uses MoneyField. However,
if you assign managers to some other attribute, you have to wrap your manager manually, like so:

    from djmoney.models.managers import money_manager
    class BankAccount(models.Model):
        
        balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

        accounts = money_manager(MyCustomManager())

Also, the money_manager wrapper only wraps the standard QuerySet methods. If you define custom
QuerySet methods, that do not end up using any of the standard ones (like "get", "filter" and so on), then
you also need to manually decorate those custom methods, like so:

    from djmoney.models.managers import understand_money

    class MyCustomQuerySet(QuerySet):
    
       @understand_money
       def my_custom_method(*args,**kwargs):
           # Awesome stuff


