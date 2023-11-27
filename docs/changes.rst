Changelog
=========


`Unreleased`_ (TBA)
-------------------

**Fixed**

- The default setting for ``CURRENCY_CHOICES`` excluded the currency choice defined by ``DEFAULT_CURRENCY``. :github-issue:`739` (`Naggafin`_)


`3.4`_ - 2023-10-17
-------------------

.. note::

   If you are using Django REST Framework or any other mechanism that relies on a custom serializer,
   please note that you now manually have to register the serializer.
   See :ref:`this code snippet <index:Note on serialization>`.

**Changed**

- Don't register Django Money serializers by default, instead the user should actively register a serializer in the ``settings.py`` :github-issue:`636` (`emorozov`_)


`3.3`_ - 2023-09-10
-------------------

**Fixed**

- Fix detection of necessary migrations. Note that this means that previously undetected migrations will be detected as of this version  :github-issue:`725` (`vanschelven`_)

`3.2`_ - 2023-07-03
-------------------

**Changed**

- Explicitly define ``id`` in ``djmoney.contrib.exchange.Rate`` model - This ensures that the database table will use ``AutoField``
  even if ``DEFAULT_AUTO_FIELD`` is set to ``BigAutoField`` in the Django project's settings #716

**Fixed**

- Downgrade asgiref to 3.6 to work with pypy3

`3.1`_ - 2023-04-20
-------------------

**Added**

- Python 3.11 support :github-issue:`700` (`sdarmofal`_)
- Django 4.2 support :github-issue:`700` (`sdarmofal`_)
- Pyright support for .pyi files :github-issue:`686` (`karolyi`_)
- Support for ``Coalesce`` :github-issue:`678` (`stianjensen`_)

**Fixed**

- Support for ``Money`` type with ``Coalesce`` in ``QuerySet.update()`` :github-issue:`678` (`stianjensen`_)
- pre-commit config for moved flake8 repo (`sdarmofal`_)
- Use latest setup-python GitHub Action :github-issue:`692` (`sondrelg`_)
- Optimize: Rate is always 1 if source and target are equal :github-issue:`689` (`nschlemm`_)
- Fixer.io backend: Avoid 403 errors :github-issue:`681` (`spaut33`_)

`3.0`_ - 2022-06-20
--------------------

**Changed**
- Update py-moneyed to 2.0. :github-issue:`638` (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Remove the deprecated ``Money.decimal_places_display`` property and argument. :github-issue:`638` (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Remove the deprecated ``CURRENCY_DECIMAL_PLACES_DISPLAY`` setting. :github-issue:`638` (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Null constraint on an implicit ``CurrencyField`` is now declared from ``null=...`` argument to ``MoneyField``. :github-issue:`638` (`antonagestam`_, `flaeppe`_, `paoloxnet`_)

**Fixed**

- Improve the internal check for whether a currency is provided :github-issue:`657` (`davidszotten`_)
- Fix test suite for django main branch :github-issue:`657` (`davidszotten`_)
- ``MoneyField`` raises ``TypeError`` when default contains a valid amount but no currence, i.e. ``Money(123, None)``. :github-issue:`661` (`flaeppe`_)
- ``MoneyField`` supports default of type ``bytes`` :github-issue:`661` (`flaeppe`_)

**Added**

- Add support for Django 4.0 and 4.1.
- Add support for Python 3.10.

**Removed**

- Drop support for Django 3.1.
- Drop support for Python 3.6.


`2.1.1`_ - 2022-01-02
---------------------

**Changed**

- Renamed ``master`` branch to ``main`` (`benjaoming`_)

**Fixed**

- Make Django REST Framework integration always raise lower-level errors as ``ValidationError``. :github-issue:`601`, :github-issue:`637` (`flaeppe`_)
- False positives in Migration changes, improvements to ``MoneyField.deconstruct``. :github-issue:`646`, :github-issue:`648` (`flaeppe`_)

`2.1`_ - 2021-09-17
-------------------

**Added**

- Add support for Django 3.2. :github-issue:`612` (`antonagestam`_)

**Removed**

- Drop support for Django 1.11, 2.1 and 3.0. :github-issue:`612` (`antonagestam`_)
- Drop support for Python 3.5. :github-issue:`612` (`antonagestam`_)

`2.0.3`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour when non-``Money`` instances are involved. :github-issue:`630` (`tned73`_)

`2.0.2`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour. :github-issue:`629` (`tned73`_)

`2.0.1`_ - 2021-07-09
---------------------

**Fixed**

- Invalid deprecation warning behavior. :github-issue:`624` (`nerdoc`_)

`2.0`_ - 2021-05-23
-------------------

**Added**

- New setting ``CURRENCY_CODE_MAX_LENGTH`` configures default max_length for MoneyField and ``exchange`` app models.

**Changed**

- BREAKING: Update ``py-moneyed`` to ``>=1.2,<2``. It uses ``babel`` to format ``Money``, which formats it differently than ``py-moneyed<1``. :github-issue:`567` (`antonagestam`_)

**Deprecated**

- ``Money.decimal_places_display`` will be removed in django-money 3.0.
- ``CURRENCY_DECIMAL_PLACES_DISPLAY`` will be removed in django-money 3.0.

`1.3.1`_ - 2021-02-04
---------------------

**Fixed**

- Do not mutate the input ``moneyed.Money`` class to ``djmoney.money.Money`` in ``MoneyField.default`` and F-expressions. :github-issue:`603` (`moser`_)

`1.3`_ - 2021-01-10
-------------------

**Added**

- Improved localization: New setting ``CURRENCY_DECIMAL_PLACES_DISPLAY`` configures decimal places to display for each configured currency. :github-issue:`521` (`wearebasti`_)

**Changed**

- Set the default value for ``models.fields.MoneyField`` to ``NOT_PROVIDED``. (`tned73`_)

**Fixed**

- Pin ``pymoneyed<1.0`` as it changed the ``repr`` output of the ``Money`` class. (`Stranger6667`_)
- Subtracting ``Money`` from ``moneyed.Money``. Regression, introduced in ``1.2``. :github-issue:`593` (`Stranger6667`_)
- Missing the right ``Money.decimal_places`` and ``Money.decimal_places_display`` values after some arithmetic operations. :github-issue:`595` (`Stranger6667`_)

`1.2.2`_ - 2020-12-29
---------------------

**Fixed**

- Confusing "number-over-money" division behavior by backporting changes from ``py-moneyed``. :github-issue:`586` (`wearebasti`_)
- ``AttributeError`` when a ``Money`` instance is divided by ``Money``. :github-issue:`585` (`niklasb`_)

`1.2.1`_ - 2020-11-29
---------------------

**Fixed**

- Aggregation through a proxy model. :github-issue:`583` (`tned73`_)

`1.2`_ - 2020-11-26
-------------------

**Fixed**

- Resulting Money object from arithmetics (add / sub / ...) inherits maximum decimal_places from arguments :github-issue:`522` (`wearebasti`_)
- ``DeprecationWarning`` related to the usage of ``cafile`` in ``urlopen``. :github-issue:`553` (`Stranger6667`_)

**Added**

- Django 3.1 support

`1.1`_ - 2020-04-06
-------------------

**Fixed**

- Optimize money operations on MoneyField instances with the same currencies. :github-issue:`541` (`horpto`_)

**Added**

- Support for ``Money`` type in ``QuerySet.bulk_update()`` :github-issue:`534` (`satels`_)

`1.0`_ - 2019-11-08
-------------------

**Added**

- Support for money descriptor customization. (`Stranger6667`_)
- Fix ``order_by()`` not returning money-compatible queryset :github-issue:`519` (`lieryan`_)
- Django 3.0 support

**Removed**

- Support for Django 1.8 & 2.0. (`Stranger6667`_)
- Support for Python 2.7. :github-issue:`515` (`benjaoming`_)
- Support for Python 3.4. (`Stranger6667`_)
- ``MoneyPatched``, use ``djmoney.money.Money`` instead. (`Stranger6667`_)

**Fixed**

- Support instances with ``decimal_places=0`` :github-issue:`509` (`fara`_)

`0.15.1`_ - 2019-06-22
----------------------

**Fixed**

- Respect field ``decimal_places`` when instantiating ``Money`` object from field db values. :github-issue:`501` (`astutejoe`_)
- Restored linting in CI tests (`benjaoming`_)

`0.15`_ - 2019-05-30
--------------------

.. warning:: This release contains backwards incompatibility, please read the release notes below.

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Remove implicit default value on non-nullable MoneyFields.
  Backwards incompatible change: set explicit ``default=0.0`` to keep previous behavior. :github-issue:`411` (`washeck`_)
- Remove support for calling ``float`` on ``Money`` instances. Use the ``amount`` attribute instead. (`Stranger6667`_)
- ``MinMoneyValidator`` and ``MaxMoneyValidator`` are not inherited from Django's ``MinValueValidator`` and ``MaxValueValidator`` anymore. :github-issue:`376`
- In model and non-model forms ``forms.MoneyField`` uses ``CURRENCY_DECIMAL_PLACES`` as the default value for ``decimal_places``. :github-issue:`434` (`Stranger6667`_, `andytwoods`_)

**Added**

- Add ``Money.decimal_places`` for per-instance configuration of decimal places in the string representation.
- Support for customization of ``CurrencyField`` length. Some cryptocurrencies could have codes longer than three characters. :github-issue:`480` (`Stranger6667`_, `MrFus10n`_)
- Add ``default_currency`` option for REST Framework field. :github-issue:`475` (`butorov`_)

**Fixed**

- Failing certificates checks when accessing 3rd party exchange rates backends.
  Fixed by adding `certifi` to the dependencies list. :github-issue:`403` (`Stranger6667`_)
- Fixed model-level ``validators`` behavior in REST Framework. :github-issue:`376` (`rapIsKal`_, `Stranger6667`_)
- Setting keyword argument ``default_currency=None`` for ``MoneyField`` did not revert to ``settings.DEFAULT_CURRENCY`` and set ``str(None)`` as database value for currency. :github-issue:`490`  (`benjaoming`_)

**Changed**

- Allow using patched ``django.core.serializers.python._get_model`` in serializers, which could be helpful for
  migrations. (`Formulka`_, `Stranger6667`_)

`0.14.4`_ - 2019-01-07
----------------------

**Changed**

- Re-raise arbitrary exceptions in JSON deserializer as `DeserializationError`. (`Stranger6667`_)

**Fixed**

- Invalid Django 1.8 version check in ``djmoney.models.fields.MoneyField.value_to_string``. (`Stranger6667`_)
- InvalidOperation in ``djmoney.contrib.django_rest_framework.fields.MoneyField.get_value`` when amount is None and currency is not None. :github-issue:`458` (`carvincarl`_)

`0.14.3`_ - 2018-08-14
----------------------

**Fixed**

- ``djmoney.forms.widgets.MoneyWidget`` decompression on Django 2.1+. :github-issue:`443` (`Stranger6667`_)

`0.14.2`_ - 2018-07-23
----------------------

**Fixed**

- Validation of ``djmoney.forms.fields.MoneyField`` when ``disabled=True`` is passed to it. :github-issue:`439` (`stinovlas`_, `Stranger6667`_)

`0.14.1`_ - 2018-07-17
----------------------

**Added**

- Support for indirect rates conversion through maximum 1 extra step (when there is no direct conversion rate:
  converting by means of a third currency for which both source and target currency have conversion
  rates). :github-issue:`425` (`Stranger6667`_, `77cc33`_)

**Fixed**

- Error was raised when trying to do a query with a `ModelWithNullableCurrency`. :github-issue:`427` (`Woile`_)

`0.14`_ - 2018-06-09
--------------------

**Added**

- Caching of exchange rates. :github-issue:`398` (`Stranger6667`_)
- Added support for nullable ``CurrencyField``. :github-issue:`260` (`Stranger6667`_)

**Fixed**

- Same currency conversion getting MissingRate exception :github-issue:`418` (`humrochagf`_)
- `TypeError` during templatetag usage inside a for loop on Django 2.0. :github-issue:`402` (`f213`_)

**Removed**

- Support for Python 3.3 :github-issue:`410` (`benjaoming`_)
- Deprecated ``choices`` argument from ``djmoney.forms.fields.MoneyField``. Use ``currency_choices`` instead. (`Stranger6667`_)

`0.13.5`_ - 2018-05-19
----------------------

**Fixed**

- Missing in dist, ``djmoney/__init__.py``. :github-issue:`417` (`benjaoming`_)

`0.13.4`_ - 2018-05-19
----------------------

**Fixed**

- Packaging of ``djmoney.contrib.exchange.management.commands``. :github-issue:`412` (`77cc33`_, `Stranger6667`_)

`0.13.3`_ - 2018-05-12
----------------------

**Added**

- Rounding support via ``round`` built-in function on Python 3. (`Stranger6667`_)

`0.13.2`_ - 2018-04-16
----------------------

**Added**

- Django Admin integration for exchange rates. :github-issue:`392` (`Stranger6667`_)

**Fixed**

- Exchange rates. TypeError when decoding JSON on Python 3.3-3.5. :github-issue:`399` (`kcyeu`_)
- Managers patching for models with custom ``Meta.default_manager_name``. :github-issue:`400` (`Stranger6667`_)

`0.13.1`_ - 2018-04-07
----------------------

**Fixed**

- Regression: Could not run w/o ``django.contrib.exchange`` :github-issue:`388` (`Stranger6667`_)

`0.13`_ - 2018-04-07
--------------------

**Added**

- Currency exchange :github-issue:`385` (`Stranger6667`_)

**Removed**

- Support for ``django-money-rates`` :github-issue:`385` (`Stranger6667`_)
- Deprecated ``Money.__float__`` which is implicitly called on some ``sum()`` operations :github-issue:`347`. (`jonashaag`_)

Migration from django-money-rates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The new application is a drop-in replacement for ``django-money-rates``.
To migrate from ``django-money-rates``:

- In ``INSTALLED_APPS`` replace ``djmoney_rates`` with ``djmoney.contrib.exchange``
- Set ``OPEN_EXCHANGE_RATES_APP_ID`` setting with your app id
- Run ``python manage.py migrate``
- Run ``python manage.py update_rates``

For more information, look at ``Working with Exchange Rates`` section in README.

`0.12.3`_ - 2017-12-13
----------------------

**Fixed**

- Fixed ``BaseMoneyValidator`` with falsy limit values. :github-issue:`371` (`1337`_)

`0.12.2`_ - 2017-12-12
----------------------

**Fixed**

- Django master branch compatibility. :github-issue:`361` (`Stranger6667`_)
- Fixed ``get_or_create`` for models with shared currency. :github-issue:`364` (`Stranger6667`_)

**Changed**

- Removed confusing rounding to integral value in ``Money.__repr__``. :github-issue:`366` (`Stranger6667`_, `evenicoulddoit`_)

`0.12.1`_ - 2017-11-20
----------------------

**Fixed**

- Fixed migrations on SQLite. :github-issue:`139`, :github-issue:`338` (`Stranger6667`_)
- Fixed ``Field.rel.to`` usage for Django 2.0. :github-issue:`349` (`richardowen`_)
- Fixed Django REST Framework behaviour for serializers without ``*_currency`` field in serializer's ``Meta.fields``. :github-issue:`351` (`elcolie`_, `Stranger6667`_)

`0.12`_ - 2017-10-22
--------------------

**Added**

- Ability to specify name for currency field. :github-issue:`195` (`Stranger6667`_)
- Validators for ``MoneyField``. :github-issue:`308` (`Stranger6667`_)

**Changed**

- Improved ``Money`` support. Now ``django-money`` fully relies on ``pymoneyed`` localization everywhere, including Django admin. :github-issue:`276` (`Stranger6667`_)
- Implement ``__html__`` method. If used in Django templates, an ``Money`` object's amount and currency are now separated with non-breaking space (``&nbsp;``) :github-issue:`337` (`jonashaag`_)

**Deprecated**

- ``djmoney.models.fields.MoneyPatched`` and ``moneyed.Money`` are deprecated. Use ``djmoney.money.Money`` instead.

**Fixed**

- Fixed model field validation. :github-issue:`308` (`Stranger6667`_).
- Fixed managers caching for Django >= 1.10. :github-issue:`318` (`Stranger6667`_).
- Fixed ``F`` expressions support for ``in`` lookups. :github-issue:`321` (`Stranger6667`_).
- Fixed money comprehension on querysets. :github-issue:`331` (`Stranger6667`_, `jaavii1988`_).
- Fixed errors in Django Admin integration. :github-issue:`334` (`Stranger6667`_, `adi-`_).

**Removed**

- Dropped support for Python 2.6 and 3.2. (`Stranger6667`_)
- Dropped support for Django 1.4, 1.5, 1.6, 1.7 and 1.9. (`Stranger6667`_)

`0.11.4`_ - 2017-06-26
----------------------

**Fixed**

- Fixed money parameters processing in update queries. :github-issue:`309` (`Stranger6667`_)

`0.11.3`_ - 2017-06-19
----------------------

**Fixed**

- Restored support for Django 1.4, 1.5, 1.6, and 1.7 & Python 2.6 :github-issue:`304` (`Stranger6667`_)

`0.11.2`_ - 2017-05-31
----------------------

**Fixed**

- Fixed field lookup regression. :github-issue:`300` (`lmdsp`_, `Stranger6667`_)

`0.11.1`_ - 2017-05-26
----------------------

**Fixed**

- Fixed access to models properties. :github-issue:`297` (`mithrilstar`_, `Stranger6667`_)

**Removed**

- Dropped support for Python 2.6. (`Stranger6667`_)
- Dropped support for Django < 1.8. (`Stranger6667`_)

`0.11`_ - 2017-05-19
--------------------

**Added**

- An ability to set custom currency choices via ``CURRENCY_CHOICES`` settings option. :github-issue:`211` (`Stranger6667`_, `ChessSpider`_)

**Fixed**

- Fixed ``AttributeError`` in ``get_or_create`` when the model have no default. :github-issue:`268` (`Stranger6667`_, `lobziik`_)
- Fixed ``UnicodeEncodeError`` in string representation of ``MoneyPatched`` on Python 2. :github-issue:`272` (`Stranger6667`_)
- Fixed various displaying errors in Django Admin . :github-issue:`232`, :github-issue:`220`, :github-issue:`196`, :github-issue:`102`, :github-issue:`90` (`Stranger6667`_,
  `arthurk`_, `mstarostik`_, `eriktelepovsky`_, `jplehmann`_, `graik`_, `benjaoming`_, `k8n`_, `yellow-sky`_)
- Fixed non-Money values support for ``in`` lookup. :github-issue:`278` (`Stranger6667`_)
- Fixed available lookups with removing of needless lookup check. :github-issue:`277` (`Stranger6667`_)
- Fixed compatibility with ``py-moneyed``. (`Stranger6667`_)
- Fixed ignored currency value in Django REST Framework integration. :github-issue:`292` (`gonzalobf`_)

`0.10.2`_ - 2017-02-18
----------------------

**Added**

- Added ability to configure decimal places output. :github-issue:`154`, :github-issue:`251` (`ivanchenkodmitry`_)

**Fixed**

- Fixed handling of ``defaults`` keyword argument in ``get_or_create`` method. :github-issue:`257` (`kjagiello`_)
- Fixed handling of currency fields lookups in ``get_or_create`` method. :github-issue:`258` (`Stranger6667`_)
- Fixed ``PendingDeprecationWarning`` during form initialization. :github-issue:`262` (`Stranger6667`_, `spookylukey`_)
- Fixed handling of ``F`` expressions which involve non-Money fields. :github-issue:`265` (`Stranger6667`_)

`0.10.1`_ - 2016-12-26
----------------------

**Fixed**

- Fixed default value for ``djmoney.forms.fields.MoneyField``. :github-issue:`249` (`tsouvarev`_)

`0.10`_ - 2016-12-19
--------------------

**Changed**

- Do not fail comparisons because of different currency. Just return ``False`` :github-issue:`225` (`benjaoming`_ and `ivirabyan`_)

**Fixed**

- Fixed ``understands_money`` behaviour. Now it can be used as a decorator :github-issue:`215` (`Stranger6667`_)
- Fixed: Not possible to revert MoneyField currency back to default :github-issue:`221` (`benjaoming`_)
- Fixed invalid ``creation_counter`` handling. :github-issue:`235` (`msgre`_ and `Stranger6667`_)
- Fixed broken field resolving. :github-issue:`241` (`Stranger6667`_)

`0.9.1`_ - 2016-08-01
---------------------

**Fixed**

- Fixed packaging.

`0.9.0`_ - 2016-07-31
---------------------

NB! If you are using custom model managers **not** named ``objects`` and you expect them to still work, please read below.

**Added**

- Support for ``Value`` and ``Func`` expressions in queries. (`Stranger6667`_)
- Support for ``in`` lookup. (`Stranger6667`_)
- Django REST Framework support. :github-issue:`179` (`Stranger6667`_)
- Django 1.10 support. :github-issue:`198` (`Stranger6667`_)
- Improved South support. (`Stranger6667`_)

**Changed**

- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. :github-issue:`199` (`spookylukey`_)
- Only make ``objects`` a MoneyManager instance automatically. :github-issue:`194` and :github-issue:`201` (`inureyes`_)

**Fixed**

- Fixed default currency value for nullable fields in forms. :github-issue:`138` (`Stranger6667`_)
- Fixed ``_has_changed`` deprecation warnings. :github-issue:`206` (`Stranger6667`_)
- Fixed ``get_or_create`` crash, when ``defaults`` is passed. :github-issue:`213` (`Stranger6667`_, `spookylukey`_)

Note about automatic model manager patches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In 0.8, Django-money automatically patches every model managers with
``MoneyManager``. This causes migration problems if two or more managers are
used in the same model.

As a side effect, other managers are also finally wrapped with ``MoneyManager``.
This effect leads Django migration to point to fields with other managers to
``MoneyManager``, and raises ``ValueError`` (``MoneyManager`` only exists as a
return of ``money_manager``, not a class-form. However migration procedure tries
to find ``MoneyManager`` to patch other managers.)

From 0.9, Django-money only patches ``objects`` with ``MoneyManager`` by default
(as documented). To patch other managers (e.g. custom managers), patch them by
wrapping with ``money_manager``.

.. code-block:: python

    from djmoney.models.managers import money_manager


    class BankAccount(models.Model):
        balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
        accounts = money_manager(MyCustomManager())

`0.8`_ - 2016-04-23
-------------------

**Added**

- Support for serialization of ``MoneyPatched`` instances in migrations. (`AlexRiina`_)
- Improved django-money-rates support. :github-issue:`173` (`Stranger6667`_)
- Extended ``F`` expressions support. (`Stranger6667`_)
- Pre-commit hooks support. (`benjaoming`_)
- Isort integration. (`Stranger6667`_)
- Makefile for common commands. (`Stranger6667`_)
- Codecov.io integration. (`Stranger6667`_)
- Python 3.5 builds to tox.ini and travis.yml. (`Stranger6667`_)
- Django master support. (`Stranger6667`_)
- Python 3.2 compatibility. (`Stranger6667`_)

**Changed**

- Refactored test suite (`Stranger6667`_)

**Fixed**

- Fixed fields caching. :github-issue:`186` (`Stranger6667`_)
- Fixed m2m fields data loss on Django < 1.8. :github-issue:`184` (`Stranger6667`_)
- Fixed managers access via instances. :github-issue:`86` (`Stranger6667`_)
- Fixed currency handling behaviour. :github-issue:`172` (`Stranger6667`_)
- Many PEP8 & flake8 fixes. (`benjaoming`_)
- Fixed filtration with ``F`` expressions. :github-issue:`174` (`Stranger6667`_)
- Fixed querying on Django 1.8+. :github-issue:`166` (`Stranger6667`_)

`0.7.6`_ - 2016-01-08
---------------------

**Added**

- Added correct paths for py.test discovery. (`benjaoming`_)
- Mention Django 1.9 in tox.ini. (`benjaoming`_)

**Fixed**

- Fix for ``get_or_create`` / ``create`` manager methods not respecting currency code. (`toudi`_)
- Fix unit tests. (`toudi`_)
- Fix for using ``MoneyField`` with ``F`` expressions when using Django >= 1.8. (`toudi`_)

`0.7.5`_ - 2015-12-22
---------------------

**Fixed**

- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` :github-issue:`149` (`browniebroke`_)
- pip instructions updated. (`GheloAce`_)

`0.7.4`_ - 2015-11-02
---------------------

**Added**

- Support for Django 1.9 (`kjagiello`_)

**Fixed**

- Fixed loaddata. (`jack-cvr`_)
- Python 2.6 fixes. (`jack-cvr`_)
- Fixed currency choices ordering. (`synotna`_)

`0.7.3`_ - 2015-10-16
---------------------

**Added**

- Sum different currencies. (`dnmellen`_)
- ``__eq__`` method. (`benjaoming`_)
- Comparison of different currencies. (`benjaoming`_)
- Default currency. (`benjaoming`_)

**Fixed**

- Fix using Choices for setting currency choices. (`benjaoming`_)
- Fix tests for Python 2.6. (`plumdog`_)

`0.7.2`_ - 2015-09-01
---------------------

**Fixed**

- Better checks on ``None`` values. (`tsouvarev`_, `sjdines`_)
- Consistency with South declarations and calling ``str`` function. (`sjdines`_)

`0.7.1`_ - 2015-08-11
---------------------

**Fixed**

- Fix bug in printing ``MoneyField``. (`YAmikep`_)
- Added fallback value for current locale getter. (`sjdines`_)

`0.7.0`_ - 2015-06-14
---------------------

**Added**

- Django 1.8 compatibility. (`willhcr`_)

`0.6.0`_ - 2015-05-23
---------------------

**Added**

- Python 3 trove classifier. (`dekkers`_)

**Changed**

- Tox cleanup. (`edwinlunando`_)
- Improved ``README``. (`glarrain`_)
- Added/Cleaned up tests. (`spookylukey`_, `AlexRiina`_)

**Fixed**

- Append ``_currency`` to non-money ExpressionFields. :github-issue:`101` (`alexhayes`_, `AlexRiina`_, `briankung`_)
- Data truncated for column. :github-issue:`103` (`alexhayes`_)
- Fixed ``has_changed`` not working. :github-issue:`95` (`spookylukey`_)
- Fixed proxy model with ``MoneyField`` returns wrong class. :github-issue:`80` (`spookylukey`_)

`0.5.0`_ - 2014-12-15
---------------------

**Added**

- Django 1.7 compatibility. (`w00kie`_)

**Fixed**

- Added ``choices=`` to instantiation of currency widget. (`davidstockwell`_)
- Nullable ``MoneyField`` should act as ``default=None``. (`jakewins`_)
- Fixed bug where a non-required ``MoneyField`` threw an exception. (`spookylukey`_)

`0.4.2`_ - 2014-07-31
---------------------
`0.4.1`_ - 2013-11-28
---------------------
`0.4.0.0`_ - 2013-11-26
-----------------------

**Added**

- Python 3 compatibility.
- tox tests.
- Format localization.
- Template tag ``money_localize``.

`0.3.4`_ - 2013-11-25
---------------------
`0.3.3.2`_ - 2013-10-31
-----------------------
`0.3.3.1`_ - 2013-10-01
-----------------------
`0.3.3`_ - 2013-02-17
---------------------

**Added**

- South support via implementing the ``south_triple_field`` method. (`mattions`_)

**Fixed**

- Fixed issues with money widget not passing attrs up to django's render method, caused id attribute to not be set in html for widgets. (`adambregenzer`_)
- Fixed issue of default currency not being passed on to widget. (`snbuchholz`_)
- Return the right default for South. (`mattions`_)
- Django 1.5 compatibility. (`devlocal`_)

`0.3.2`_ - 2012-11-30
---------------------

**Fixed**

- Fixed issues with ``display_for_field`` not detecting fields correctly. (`adambregenzer`_)
- Added South ignore rule to avoid duplicate currency field when using the frozen ORM. (`rach`_)
- Disallow override of objects manager if not setting it up with an instance. (`rach`_)

`0.3.1`_ - 2012-10-11
---------------------

**Fixed**

- Fix ``AttributeError`` when Model inherit a manager. (`rach`_)
- Correctly serialize the field. (`akumria`_)

`0.3`_ - 2012-09-30
-------------------

**Added**

- Allow django-money to be specified as read-only in a model. (`akumria`_)
- South support: Declare default attribute values. (`pjdelport`_)

`0.2`_ - 2012-04-10
-------------------

- Initial public release

.. _Unreleased: https:///github.com/django-money/django-money/compare/3.4...HEAD

.. _3.4: https:///github.com/django-money/django-money/compare/3.3...3.4
.. _3.3: https:///github.com/django-money/django-money/compare/3.2...3.3
.. _3.2: https:///github.com/django-money/django-money/compare/3.1...3.2
.. _3.1: https:///github.com/django-money/django-money/compare/3.0...3.1
.. _3.0: https:///github.com/django-money/django-money/compare/2.1.1...3.0
.. _2.1.1: https:///github.com/django-money/django-money/compare/2.1...2.1.1
.. _2.1: https:///github.com/django-money/django-money/compare/2.0.3...2.1
.. _2.0.3: https://github.com/django-money/django-money/compare/2.0.2...2.0.3
.. _2.0.2: https://github.com/django-money/django-money/compare/2.0.1...2.0.2
.. _2.0.1: https://github.com/django-money/django-money/compare/2.0...2.0.1
.. _2.0: https://github.com/django-money/django-money/compare/1.3.1...2.0
.. _1.3.1: https://github.com/django-money/django-money/compare/1.3...1.3.1
.. _1.3: https://github.com/django-money/django-money/compare/1.2.2...1.3
.. _1.2.2: https://github.com/django-money/django-money/compare/1.2.1...1.2.2
.. _1.2.1: https://github.com/django-money/django-money/compare/1.2...1.2.1
.. _1.2: https://github.com/django-money/django-money/compare/1.1...1.2
.. _1.1: https://github.com/django-money/django-money/compare/1.0...1.1
.. _1.0: https://github.com/django-money/django-money/compare/0.15.1...1.0
.. _0.15.1: https://github.com/django-money/django-money/compare/0.15.1...0.15
.. _0.15: https://github.com/django-money/django-money/compare/0.15...0.14.4
.. _0.14.4: https://github.com/django-money/django-money/compare/0.14.4...0.14.3
.. _0.14.3: https://github.com/django-money/django-money/compare/0.14.3...0.14.2
.. _0.14.2: https://github.com/django-money/django-money/compare/0.14.2...0.14.1
.. _0.14.1: https://github.com/django-money/django-money/compare/0.14.1...0.14
.. _0.14: https://github.com/django-money/django-money/compare/0.14...0.13.5
.. _0.13.5: https://github.com/django-money/django-money/compare/0.13.4...0.13.5
.. _0.13.4: https://github.com/django-money/django-money/compare/0.13.3...0.13.4
.. _0.13.3: https://github.com/django-money/django-money/compare/0.13.2...0.13.3
.. _0.13.2: https://github.com/django-money/django-money/compare/0.13.1...0.13.2
.. _0.13.1: https://github.com/django-money/django-money/compare/0.13...0.13.1
.. _0.13: https://github.com/django-money/django-money/compare/0.12.3...0.13
.. _0.12.3: https://github.com/django-money/django-money/compare/0.12.2...0.12.3
.. _0.12.2: https://github.com/django-money/django-money/compare/0.12.1...0.12.2
.. _0.12.1: https://github.com/django-money/django-money/compare/0.12...0.12.1
.. _0.12: https://github.com/django-money/django-money/compare/0.11.4...0.12
.. _0.11.4: https://github.com/django-money/django-money/compare/0.11.3...0.11.4
.. _0.11.3: https://github.com/django-money/django-money/compare/0.11.2...0.11.3
.. _0.11.2: https://github.com/django-money/django-money/compare/0.11.1...0.11.2
.. _0.11.1: https://github.com/django-money/django-money/compare/0.11...0.11.1
.. _0.11: https://github.com/django-money/django-money/compare/0.10.2...0.11
.. _0.10.2: https://github.com/django-money/django-money/compare/0.10.1...0.10.2
.. _0.10.1: https://github.com/django-money/django-money/compare/0.10...0.10.1
.. _0.10: https://github.com/django-money/django-money/compare/0.9.1...0.10
.. _0.9.1: https://github.com/django-money/django-money/compare/0.9.0...0.9.1
.. _0.9.0: https://github.com/django-money/django-money/compare/0.8...0.9.0
.. _0.8: https://github.com/django-money/django-money/compare/0.7.6...0.8
.. _0.7.6: https://github.com/django-money/django-money/compare/0.7.5...0.7.6
.. _0.7.5: https://github.com/django-money/django-money/compare/0.7.4...0.7.5
.. _0.7.4: https://github.com/django-money/django-money/compare/0.7.3...0.7.4
.. _0.7.3: https://github.com/django-money/django-money/compare/0.7.2...0.7.3
.. _0.7.2: https://github.com/django-money/django-money/compare/0.7.1...0.7.2
.. _0.7.1: https://github.com/django-money/django-money/compare/0.7.0...0.7.1
.. _0.7.0: https://github.com/django-money/django-money/compare/0.6.0...0.7.0
.. _0.6.0: https://github.com/django-money/django-money/compare/0.5.0...0.6.0
.. _0.5.0: https://github.com/django-money/django-money/compare/0.4.2...0.5.0
.. _0.4.2: https://github.com/django-money/django-money/compare/0.4.1...0.4.2
.. _0.4.1: https://github.com/django-money/django-money/compare/0.4.0.0...0.4.1
.. _0.4.0.0: https://github.com/django-money/django-money/compare/0.3.4...0.4.0.0
.. _0.3.4: https://github.com/django-money/django-money/compare/0.3.3.2...0.3.4
.. _0.3.3.2: https://github.com/django-money/django-money/compare/0.3.3.1...0.3.3.2
.. _0.3.3.1: https://github.com/django-money/django-money/compare/0.3.3...0.3.3.1
.. _0.3.3: https://github.com/django-money/django-money/compare/0.3.2...0.3.3
.. _0.3.2: https://github.com/django-money/django-money/compare/0.3.1...0.3.2
.. _0.3.1: https://github.com/django-money/django-money/compare/0.3...0.3.1
.. _0.3: https://github.com/django-money/django-money/compare/0.2...0.3
.. _0.2: https://github.com/django-money/django-money/compare/0.2...a6d90348085332a393abb40b86b5dd9505489b04

.. _77cc33: https://github.com/77cc33
.. _AlexRiina: https://github.com/AlexRiina
.. _carvincarl: https://github.com/carvincarl
.. _ChessSpider: https://github.com/ChessSpider
.. _GheloAce: https://github.com/GheloAce
.. _Stranger6667: https://github.com/Stranger6667
.. _YAmikep: https://github.com/YAmikep
.. _adambregenzer: https://github.com/adambregenzer
.. _adi-: https://github.com/adi-
.. _akumria: https://github.com/akumria
.. _alexhayes: https://github.com/alexhayes
.. _andytwoods: https://github.com/andytwoods
.. _antonagestam: https://github.com/antonagestam
.. _arthurk: https://github.com/arthurk
.. _astutejoe: https://github.com/astutejoe
.. _benjaoming: https://github.com/benjaoming
.. _briankung: https://github.com/briankung
.. _browniebroke: https://github.com/browniebroke
.. _butorov: https://github.com/butorov
.. _davidstockwell: https://github.com/davidstockwell
.. _dekkers: https://github.com/dekkers
.. _devlocal: https://github.com/devlocal
.. _dnmellen: https://github.com/dnmellen
.. _edwinlunando: https://github.com/edwinlunando
.. _elcolie: https://github.com/elcolie
.. _emorozov: https://github.com/emorozov
.. _eriktelepovsky: https://github.com/eriktelepovsky
.. _evenicoulddoit: https://github.com/evenicoulddoit
.. _f213: https://github.com/f213
.. _flaeppe: https://github.com/flaeppe
.. _Formulka: https://github.com/Formulka
.. _glarrain: https://github.com/glarrain
.. _graik: https://github.com/graik
.. _gonzalobf: https://github.com/gonzalobf
.. _horpto: https://github.com/horpto
.. _inureyes: https://github.com/inureyes
.. _ivanchenkodmitry: https://github.com/ivanchenkodmitry
.. _jaavii1988: https://github.com/jaavii1988
.. _jack-cvr: https://github.com/jack-cvr
.. _jakewins: https://github.com/jakewins
.. _jonashaag: https://github.com/jonashaag
.. _jplehmann: https://github.com/jplehmann
.. _karolyi: https://github.com/karolyi
.. _kcyeu: https://github.com/kcyeu
.. _kjagiello: https://github.com/kjagiello
.. _ivirabyan: https://github.com/ivirabyan
.. _k8n: https://github.com/k8n
.. _lmdsp: https://github.com/lmdsp
.. _lieryan: https://github.com/lieryan
.. _lobziik: https://github.com/lobziik
.. _mattions: https://github.com/mattions
.. _mithrilstar: https://github.com/mithrilstar
.. _moser: https://github.com/moser
.. _MrFus10n: https://github.com/MrFus10n
.. _msgre: https://github.com/msgre
.. _mstarostik: https://github.com/mstarostik
.. _Naggafin: https://github.com/Naggafin
.. _niklasb: https://github.com/niklasb
.. _nerdoc: https://github.com/nerdoc
.. _nschlemm: https://github.com/nschlemm
.. _paoloxnet: https://github.com/paoloxnet
.. _pjdelport: https://github.com/pjdelport
.. _plumdog: https://github.com/plumdog
.. _rach: https://github.com/rach
.. _rapIsKal: https://github.com/rapIsKal
.. _richardowen: https://github.com/richardowen
.. _satels: https://github.com/satels
.. _sdarmofal: https://github.com/sdarmofal
.. _sjdines: https://github.com/sjdines
.. _snbuchholz: https://github.com/snbuchholz
.. _sondrelg: https://github.com/sondrelg
.. _spaut33: https://github.com/spaut33
.. _spookylukey: https://github.com/spookylukey
.. _stianjensen: https://github.com/stianjensen
.. _stinovlas: https://github.com/stinovlas
.. _synotna: https://github.com/synotna
.. _tned73: https://github.com/tned73
.. _toudi: https://github.com/toudi
.. _tsouvarev: https://github.com/tsouvarev
.. _yellow-sky: https://github.com/yellow-sky
.. _Woile: https://github.com/Woile
.. _w00kie: https://github.com/w00kie
.. _willhcr: https://github.com/willhcr
.. _1337: https://github.com/1337
.. _humrochagf: https://github.com/humrochagf
.. _washeck: https://github.com/washeck
.. _fara: https://github.com/fara
.. _wearebasti: https://github.com/wearebasti
.. _davidszotten: https://github.com/davidszotten
.. _vanschelven: https://github.com/vanschelven
