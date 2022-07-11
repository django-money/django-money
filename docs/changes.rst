Changelog
=========

`Unreleased`_ - TBA
-------------------

**Fixed**

- Support for ``Money`` type with ``Coalesce`` in ``QuerySet.update()`` `#678`_ (`stianjensen`_)


`3.0`_ - 2022-06-20
--------------------

**Changed**
- Update py-moneyed to 2.0. `#638`_ (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Remove the deprecated ``Money.decimal_places_display`` property and argument. `#638`_ (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Remove the deprecated ``CURRENCY_DECIMAL_PLACES_DISPLAY`` setting. `#638`_ (`antonagestam`_, `flaeppe`_, `paoloxnet`_)
- Null constraint on an implicit ``CurrencyField`` is now declared from ``null=...`` argument to ``MoneyField``. `#638`_ (`antonagestam`_, `flaeppe`_, `paoloxnet`_)

**Fixed**

- Improve the internal check for whether a currency is provided `#657`_ (`davidszotten`_)
- Fix test suite for django main branch `#657`_ (`davidszotten`_)
- ``MoneyField`` raises ``TypeError`` when default contains a valid amount but no currence, i.e. ``Money(123, None)``. `#661`_ (`flaeppe`_)
- ``MoneyField`` supports default of type ``bytes`` `#661`_ (`flaeppe`_)

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

- Make Django REST Framework integration always raise lower-level errors as ``ValidationError``. `#601`_, `#637`_ (`flaeppe`_)
- False positives in Migration changes, improvements to ``MoneyField.deconstruct``. `#646`_, `#648`_ (`flaeppe`_)

`2.1`_ - 2021-09-17
-------------------

**Added**

- Add support for Django 3.2. `#612`_ (`antonagestam`_)

**Removed**

- Drop support for Django 1.11, 2.1 and 3.0. `#612`_ (`antonagestam`_)
- Drop support for Python 3.5. `#612`_ (`antonagestam`_)

`2.0.3`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour when non-``Money`` instances are involved. `#630`_ (`tned73`_)

`2.0.2`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour. `#629`_ (`tned73`_)

`2.0.1`_ - 2021-07-09
---------------------

**Fixed**

- Invalid deprecation warning behavior. `#624`_ (`nerdoc`_)

`2.0`_ - 2021-05-23
-------------------

**Added**

- New setting ``CURRENCY_CODE_MAX_LENGTH`` configures default max_length for MoneyField and ``exchange`` app models.

**Changed**

- BREAKING: Update ``py-moneyed`` to ``>=1.2,<2``. It uses ``babel`` to format ``Money``, which formats it differently than ``py-moneyed<1``. `#567`_ (`antonagestam`_)

**Deprecated**

- ``Money.decimal_places_display`` will be removed in django-money 3.0.
- ``CURRENCY_DECIMAL_PLACES_DISPLAY`` will be removed in django-money 3.0.

`1.3.1`_ - 2021-02-04
---------------------

**Fixed**

- Do not mutate the input ``moneyed.Money`` class to ``djmoney.money.Money`` in ``MoneyField.default`` and F-expressions. `#603`_ (`moser`_)

`1.3`_ - 2021-01-10
-------------------

**Added**

- Improved localization: New setting ``CURRENCY_DECIMAL_PLACES_DISPLAY`` configures decimal places to display for each configured currency. `#521`_ (`wearebasti`_)

**Changed**

- Set the default value for ``models.fields.MoneyField`` to ``NOT_PROVIDED``. (`tned73`_)

**Fixed**

- Pin ``pymoneyed<1.0`` as it changed the ``repr`` output of the ``Money`` class. (`Stranger6667`_)
- Subtracting ``Money`` from ``moneyed.Money``. Regression, introduced in ``1.2``. `#593`_ (`Stranger6667`_)
- Missing the right ``Money.decimal_places`` and ``Money.decimal_places_display`` values after some arithmetic operations. `#595`_ (`Stranger6667`_)

`1.2.2`_ - 2020-12-29
---------------------

**Fixed**

- Confusing "number-over-money" division behavior by backporting changes from ``py-moneyed``. `#586`_ (`wearebasti`_)
- ``AttributeError`` when a ``Money`` instance is divided by ``Money``. `#585`_ (`niklasb`_)

`1.2.1`_ - 2020-11-29
---------------------

**Fixed**

- Aggregation through a proxy model. `#583`_ (`tned73`_)

`1.2`_ - 2020-11-26
-------------------

**Fixed**

- Resulting Money object from arithmetics (add / sub / ...) inherits maximum decimal_places from arguments `#522`_ (`wearebasti`_)
- ``DeprecationWarning`` related to the usage of ``cafile`` in ``urlopen``. `#553`_ (`Stranger6667`_)

**Added**

- Django 3.1 support

`1.1`_ - 2020-04-06
-------------------

**Fixed**

- Optimize money operations on MoneyField instances with the same currencies. `#541`_ (`horpto`_)

**Added**

- Support for ``Money`` type in ``QuerySet.bulk_update()`` `#534`_ (`satels`_)

`1.0`_ - 2019-11-08
-------------------

**Added**

- Support for money descriptor customization. (`Stranger6667`_)
- Fix ``order_by()`` not returning money-compatible queryset `#519`_ (`lieryan`_)
- Django 3.0 support

**Removed**

- Support for Django 1.8 & 2.0. (`Stranger6667`_)
- Support for Python 2.7. `#515`_ (`benjaoming`_)
- Support for Python 3.4. (`Stranger6667`_)
- ``MoneyPatched``, use ``djmoney.money.Money`` instead. (`Stranger6667`_)

**Fixed**

- Support instances with ``decimal_places=0`` `#509`_ (`fara`_)

`0.15.1`_ - 2019-06-22
----------------------

**Fixed**

- Respect field ``decimal_places`` when instantiating ``Money`` object from field db values. `#501`_ (`astutejoe`_)
- Restored linting in CI tests (`benjaoming`_)

`0.15`_ - 2019-05-30
--------------------

.. warning:: This release contains backwards incompatibility, please read the release notes below.

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Remove implicit default value on non-nullable MoneyFields.
  Backwards incompatible change: set explicit ``default=0.0`` to keep previous behavior. `#411`_ (`washeck`_)
- Remove support for calling ``float`` on ``Money`` instances. Use the ``amount`` attribute instead. (`Stranger6667`_)
- ``MinMoneyValidator`` and ``MaxMoneyValidator`` are not inherited from Django's ``MinValueValidator`` and ``MaxValueValidator`` anymore. `#376`_
- In model and non-model forms ``forms.MoneyField`` uses ``CURRENCY_DECIMAL_PLACES`` as the default value for ``decimal_places``. `#434`_ (`Stranger6667`_, `andytwoods`_)

**Added**

- Add ``Money.decimal_places`` for per-instance configuration of decimal places in the string representation.
- Support for customization of ``CurrencyField`` length. Some cryptocurrencies could have codes longer than three characters. `#480`_ (`Stranger6667`_, `MrFus10n`_)
- Add ``default_currency`` option for REST Framework field. `#475`_ (`butorov`_)

**Fixed**

- Failing certificates checks when accessing 3rd party exchange rates backends.
  Fixed by adding `certifi` to the dependencies list. `#403`_ (`Stranger6667`_)
- Fixed model-level ``validators`` behavior in REST Framework. `#376`_ (`rapIsKal`_, `Stranger6667`_)
- Setting keyword argument ``default_currency=None`` for ``MoneyField`` did not revert to ``settings.DEFAULT_CURRENCY`` and set ``str(None)`` as database value for currency. `#490`_  (`benjaoming`_)

**Changed**

- Allow using patched ``django.core.serializers.python._get_model`` in serializers, which could be helpful for
  migrations. (`Formulka`_, `Stranger6667`_)

`0.14.4`_ - 2019-01-07
----------------------

**Changed**

- Re-raise arbitrary exceptions in JSON deserializer as `DeserializationError`. (`Stranger6667`_)

**Fixed**

- Invalid Django 1.8 version check in ``djmoney.models.fields.MoneyField.value_to_string``. (`Stranger6667`_)
- InvalidOperation in ``djmoney.contrib.django_rest_framework.fields.MoneyField.get_value`` when amount is None and currency is not None. `#458`_ (`carvincarl`_)

`0.14.3`_ - 2018-08-14
----------------------

**Fixed**

- ``djmoney.forms.widgets.MoneyWidget`` decompression on Django 2.1+. `#443`_ (`Stranger6667`_)

`0.14.2`_ - 2018-07-23
----------------------

**Fixed**

- Validation of ``djmoney.forms.fields.MoneyField`` when ``disabled=True`` is passed to it. `#439`_ (`stinovlas`_, `Stranger6667`_)

`0.14.1`_ - 2018-07-17
----------------------

**Added**

- Support for indirect rates conversion through maximum 1 extra step (when there is no direct conversion rate:
  converting by means of a third currency for which both source and target currency have conversion
  rates). `#425`_ (`Stranger6667`_, `77cc33`_)

**Fixed**

- Error was raised when trying to do a query with a `ModelWithNullableCurrency`. `#427`_ (`Woile`_)

`0.14`_ - 2018-06-09
--------------------

**Added**

- Caching of exchange rates. `#398`_ (`Stranger6667`_)
- Added support for nullable ``CurrencyField``. `#260`_ (`Stranger6667`_)

**Fixed**

- Same currency conversion getting MissingRate exception `#418`_ (`humrochagf`_)
- `TypeError` during templatetag usage inside a for loop on Django 2.0. `#402`_ (`f213`_)

**Removed**

- Support for Python 3.3 `#410`_ (`benjaoming`_)
- Deprecated ``choices`` argument from ``djmoney.forms.fields.MoneyField``. Use ``currency_choices`` instead. (`Stranger6667`_)

`0.13.5`_ - 2018-05-19
----------------------

**Fixed**

- Missing in dist, ``djmoney/__init__.py``. `#417`_ (`benjaoming`_)

`0.13.4`_ - 2018-05-19
----------------------

**Fixed**

- Packaging of ``djmoney.contrib.exchange.management.commands``. `#412`_ (`77cc33`_, `Stranger6667`_)

`0.13.3`_ - 2018-05-12
----------------------

**Added**

- Rounding support via ``round`` built-in function on Python 3. (`Stranger6667`_)

`0.13.2`_ - 2018-04-16
----------------------

**Added**

- Django Admin integration for exchange rates. `#392`_ (`Stranger6667`_)

**Fixed**

- Exchange rates. TypeError when decoding JSON on Python 3.3-3.5. `#399`_ (`kcyeu`_)
- Managers patching for models with custom ``Meta.default_manager_name``. `#400`_ (`Stranger6667`_)

`0.13.1`_ - 2018-04-07
----------------------

**Fixed**

- Regression: Could not run w/o ``django.contrib.exchange`` `#388`_ (`Stranger6667`_)

`0.13`_ - 2018-04-07
--------------------

**Added**

- Currency exchange `#385`_ (`Stranger6667`_)

**Removed**

- Support for ``django-money-rates`` `#385`_ (`Stranger6667`_)
- Deprecated ``Money.__float__`` which is implicitly called on some ``sum()`` operations `#347`_. (`jonashaag`_)

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

- Fixed ``BaseMoneyValidator`` with falsy limit values. `#371`_ (`1337`_)

`0.12.2`_ - 2017-12-12
----------------------

**Fixed**

- Django master branch compatibility. `#361`_ (`Stranger6667`_)
- Fixed ``get_or_create`` for models with shared currency. `#364`_ (`Stranger6667`_)

**Changed**

- Removed confusing rounding to integral value in ``Money.__repr__``. `#366`_ (`Stranger6667`_, `evenicoulddoit`_)

`0.12.1`_ - 2017-11-20
----------------------

**Fixed**

- Fixed migrations on SQLite. `#139`_, `#338`_ (`Stranger6667`_)
- Fixed ``Field.rel.to`` usage for Django 2.0. `#349`_ (`richardowen`_)
- Fixed Django REST Framework behaviour for serializers without ``*_currency`` field in serializer's ``Meta.fields``. `#351`_ (`elcolie`_, `Stranger6667`_)

`0.12`_ - 2017-10-22
--------------------

**Added**

- Ability to specify name for currency field. `#195`_ (`Stranger6667`_)
- Validators for ``MoneyField``. `#308`_ (`Stranger6667`_)

**Changed**

- Improved ``Money`` support. Now ``django-money`` fully relies on ``pymoneyed`` localization everywhere, including Django admin. `#276`_ (`Stranger6667`_)
- Implement ``__html__`` method. If used in Django templates, an ``Money`` object's amount and currency are now separated with non-breaking space (``&nbsp;``) `#337`_ (`jonashaag`_)

**Deprecated**

- ``djmoney.models.fields.MoneyPatched`` and ``moneyed.Money`` are deprecated. Use ``djmoney.money.Money`` instead.

**Fixed**

- Fixed model field validation. `#308`_ (`Stranger6667`_).
- Fixed managers caching for Django >= 1.10. `#318`_ (`Stranger6667`_).
- Fixed ``F`` expressions support for ``in`` lookups. `#321`_ (`Stranger6667`_).
- Fixed money comprehension on querysets. `#331`_ (`Stranger6667`_, `jaavii1988`_).
- Fixed errors in Django Admin integration. `#334`_ (`Stranger6667`_, `adi-`_).

**Removed**

- Dropped support for Python 2.6 and 3.2. (`Stranger6667`_)
- Dropped support for Django 1.4, 1.5, 1.6, 1.7 and 1.9. (`Stranger6667`_)

`0.11.4`_ - 2017-06-26
----------------------

**Fixed**

- Fixed money parameters processing in update queries. `#309`_ (`Stranger6667`_)

`0.11.3`_ - 2017-06-19
----------------------

**Fixed**

- Restored support for Django 1.4, 1.5, 1.6, and 1.7 & Python 2.6 `#304`_ (`Stranger6667`_)

`0.11.2`_ - 2017-05-31
----------------------

**Fixed**

- Fixed field lookup regression. `#300`_ (`lmdsp`_, `Stranger6667`_)

`0.11.1`_ - 2017-05-26
----------------------

**Fixed**

- Fixed access to models properties. `#297`_ (`mithrilstar`_, `Stranger6667`_)

**Removed**

- Dropped support for Python 2.6. (`Stranger6667`_)
- Dropped support for Django < 1.8. (`Stranger6667`_)

`0.11`_ - 2017-05-19
--------------------

**Added**

- An ability to set custom currency choices via ``CURRENCY_CHOICES`` settings option. `#211`_ (`Stranger6667`_, `ChessSpider`_)

**Fixed**

- Fixed ``AttributeError`` in ``get_or_create`` when the model have no default. `#268`_ (`Stranger6667`_, `lobziik`_)
- Fixed ``UnicodeEncodeError`` in string representation of ``MoneyPatched`` on Python 2. `#272`_ (`Stranger6667`_)
- Fixed various displaying errors in Django Admin . `#232`_, `#220`_, `#196`_, `#102`_, `#90`_ (`Stranger6667`_,
  `arthurk`_, `mstarostik`_, `eriktelepovsky`_, `jplehmann`_, `graik`_, `benjaoming`_, `k8n`_, `yellow-sky`_)
- Fixed non-Money values support for ``in`` lookup. `#278`_ (`Stranger6667`_)
- Fixed available lookups with removing of needless lookup check. `#277`_ (`Stranger6667`_)
- Fixed compatibility with ``py-moneyed``. (`Stranger6667`_)
- Fixed ignored currency value in Django REST Framework integration. `#292`_ (`gonzalobf`_)

`0.10.2`_ - 2017-02-18
----------------------

**Added**

- Added ability to configure decimal places output. `#154`_, `#251`_ (`ivanchenkodmitry`_)

**Fixed**

- Fixed handling of ``defaults`` keyword argument in ``get_or_create`` method. `#257`_ (`kjagiello`_)
- Fixed handling of currency fields lookups in ``get_or_create`` method. `#258`_ (`Stranger6667`_)
- Fixed ``PendingDeprecationWarning`` during form initialization. `#262`_ (`Stranger6667`_, `spookylukey`_)
- Fixed handling of ``F`` expressions which involve non-Money fields. `#265`_ (`Stranger6667`_)

`0.10.1`_ - 2016-12-26
----------------------

**Fixed**

- Fixed default value for ``djmoney.forms.fields.MoneyField``. `#249`_ (`tsouvarev`_)

`0.10`_ - 2016-12-19
--------------------

**Changed**

- Do not fail comparisons because of different currency. Just return ``False`` `#225`_ (`benjaoming`_ and `ivirabyan`_)

**Fixed**

- Fixed ``understands_money`` behaviour. Now it can be used as a decorator `#215`_ (`Stranger6667`_)
- Fixed: Not possible to revert MoneyField currency back to default `#221`_ (`benjaoming`_)
- Fixed invalid ``creation_counter`` handling. `#235`_ (`msgre`_ and `Stranger6667`_)
- Fixed broken field resolving. `#241`_ (`Stranger6667`_)

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
- Django REST Framework support. `#179`_ (`Stranger6667`_)
- Django 1.10 support. `#198`_ (`Stranger6667`_)
- Improved South support. (`Stranger6667`_)

**Changed**

- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. `#199`_ (`spookylukey`_)
- Only make ``objects`` a MoneyManager instance automatically. `#194`_ and `#201`_ (`inureyes`_)

**Fixed**

- Fixed default currency value for nullable fields in forms. `#138`_ (`Stranger6667`_)
- Fixed ``_has_changed`` deprecation warnings. `#206`_ (`Stranger6667`_)
- Fixed ``get_or_create`` crash, when ``defaults`` is passed. `#213`_ (`Stranger6667`_, `spookylukey`_)

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
- Improved django-money-rates support. `#173`_ (`Stranger6667`_)
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

- Fixed fields caching. `#186`_ (`Stranger6667`_)
- Fixed m2m fields data loss on Django < 1.8. `#184`_ (`Stranger6667`_)
- Fixed managers access via instances. `#86`_ (`Stranger6667`_)
- Fixed currency handling behaviour. `#172`_ (`Stranger6667`_)
- Many PEP8 & flake8 fixes. (`benjaoming`_)
- Fixed filtration with ``F`` expressions. `#174`_ (`Stranger6667`_)
- Fixed querying on Django 1.8+. `#166`_ (`Stranger6667`_)

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

- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` `#149`_ (`browniebroke`_)
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

- Append ``_currency`` to non-money ExpressionFields. `#101`_ (`alexhayes`_, `AlexRiina`_, `briankung`_)
- Data truncated for column. `#103`_ (`alexhayes`_)
- Fixed ``has_changed`` not working. `#95`_ (`spookylukey`_)
- Fixed proxy model with ``MoneyField`` returns wrong class. `#80`_ (`spookylukey`_)

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

.. _Unreleased: https:///github.com/django-money/django-money/compare/3.0...HEAD
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

.. _#661: https://github.com/django-money/django-money/issues/657
.. _#657: https://github.com/django-money/django-money/issues/657
.. _#648: https://github.com/django-money/django-money/issues/648
.. _#646: https://github.com/django-money/django-money/issues/646
.. _#638: https://github.com/django-money/django-money/issues/638
.. _#637: https://github.com/django-money/django-money/issues/637
.. _#630: https://github.com/django-money/django-money/pull/630
.. _#629: https://github.com/django-money/django-money/pull/629
.. _#624: https://github.com/django-money/django-money/issues/624
.. _#612: https://github.com/django-money/django-money/pull/612
.. _#603: https://github.com/django-money/django-money/issues/603
.. _#601: https://github.com/django-money/django-money/issues/601
.. _#595: https://github.com/django-money/django-money/issues/595
.. _#593: https://github.com/django-money/django-money/issues/593
.. _#586: https://github.com/django-money/django-money/issues/586
.. _#585: https://github.com/django-money/django-money/pull/585
.. _#583: https://github.com/django-money/django-money/issues/583
.. _#567: https://github.com/django-money/django-money/issues/567
.. _#553: https://github.com/django-money/django-money/issues/553
.. _#541: https://github.com/django-money/django-money/issues/541
.. _#534: https://github.com/django-money/django-money/issues/534
.. _#515: https://github.com/django-money/django-money/issues/515
.. _#509: https://github.com/django-money/django-money/issues/509
.. _#501: https://github.com/django-money/django-money/issues/501
.. _#490: https://github.com/django-money/django-money/issues/490
.. _#475: https://github.com/django-money/django-money/issues/475
.. _#480: https://github.com/django-money/django-money/issues/480
.. _#458: https://github.com/django-money/django-money/issues/458
.. _#443: https://github.com/django-money/django-money/issues/443
.. _#439: https://github.com/django-money/django-money/issues/439
.. _#434: https://github.com/django-money/django-money/issues/434
.. _#427: https://github.com/django-money/django-money/pull/427
.. _#425: https://github.com/django-money/django-money/issues/425
.. _#417: https://github.com/django-money/django-money/issues/417
.. _#412: https://github.com/django-money/django-money/issues/412
.. _#410: https://github.com/django-money/django-money/issues/410
.. _#403: https://github.com/django-money/django-money/issues/403
.. _#402: https://github.com/django-money/django-money/issues/402
.. _#400: https://github.com/django-money/django-money/issues/400
.. _#399: https://github.com/django-money/django-money/issues/399
.. _#398: https://github.com/django-money/django-money/issues/398
.. _#392: https://github.com/django-money/django-money/issues/392
.. _#388: https://github.com/django-money/django-money/issues/388
.. _#385: https://github.com/django-money/django-money/issues/385
.. _#376: https://github.com/django-money/django-money/issues/376
.. _#347: https://github.com/django-money/django-money/issues/347
.. _#371: https://github.com/django-money/django-money/issues/371
.. _#366: https://github.com/django-money/django-money/issues/366
.. _#364: https://github.com/django-money/django-money/issues/364
.. _#361: https://github.com/django-money/django-money/issues/361
.. _#351: https://github.com/django-money/django-money/issues/351
.. _#349: https://github.com/django-money/django-money/pull/349
.. _#338: https://github.com/django-money/django-money/issues/338
.. _#337: https://github.com/django-money/django-money/issues/337
.. _#334: https://github.com/django-money/django-money/issues/334
.. _#331: https://github.com/django-money/django-money/issues/331
.. _#321: https://github.com/django-money/django-money/issues/321
.. _#318: https://github.com/django-money/django-money/issues/318
.. _#309: https://github.com/django-money/django-money/issues/309
.. _#308: https://github.com/django-money/django-money/issues/308
.. _#304: https://github.com/django-money/django-money/issues/304
.. _#300: https://github.com/django-money/django-money/issues/300
.. _#297: https://github.com/django-money/django-money/issues/297
.. _#292: https://github.com/django-money/django-money/issues/292
.. _#278: https://github.com/django-money/django-money/issues/278
.. _#277: https://github.com/django-money/django-money/issues/277
.. _#276: https://github.com/django-money/django-money/issues/276
.. _#272: https://github.com/django-money/django-money/issues/272
.. _#268: https://github.com/django-money/django-money/issues/268
.. _#265: https://github.com/django-money/django-money/issues/265
.. _#262: https://github.com/django-money/django-money/issues/262
.. _#260: https://github.com/django-money/django-money/issues/260
.. _#258: https://github.com/django-money/django-money/issues/258
.. _#257: https://github.com/django-money/django-money/pull/257
.. _#251: https://github.com/django-money/django-money/pull/251
.. _#249: https://github.com/django-money/django-money/pull/249
.. _#241: https://github.com/django-money/django-money/issues/241
.. _#235: https://github.com/django-money/django-money/issues/235
.. _#232: https://github.com/django-money/django-money/issues/232
.. _#225: https://github.com/django-money/django-money/issues/225
.. _#221: https://github.com/django-money/django-money/issues/221
.. _#220: https://github.com/django-money/django-money/issues/220
.. _#215: https://github.com/django-money/django-money/issues/215
.. _#213: https://github.com/django-money/django-money/issues/213
.. _#211: https://github.com/django-money/django-money/issues/211
.. _#206: https://github.com/django-money/django-money/issues/206
.. _#201: https://github.com/django-money/django-money/issues/201
.. _#199: https://github.com/django-money/django-money/issues/199
.. _#198: https://github.com/django-money/django-money/issues/198
.. _#196: https://github.com/django-money/django-money/issues/196
.. _#195: https://github.com/django-money/django-money/issues/195
.. _#194: https://github.com/django-money/django-money/issues/194
.. _#186: https://github.com/django-money/django-money/issues/186
.. _#184: https://github.com/django-money/django-money/issues/184
.. _#179: https://github.com/django-money/django-money/issues/179
.. _#174: https://github.com/django-money/django-money/issues/174
.. _#173: https://github.com/django-money/django-money/issues/173
.. _#172: https://github.com/django-money/django-money/issues/172
.. _#166: https://github.com/django-money/django-money/issues/166
.. _#154: https://github.com/django-money/django-money/issues/154
.. _#149: https://github.com/django-money/django-money/issues/149
.. _#139: https://github.com/django-money/django-money/issues/139
.. _#138: https://github.com/django-money/django-money/issues/138
.. _#103: https://github.com/django-money/django-money/issues/103
.. _#102: https://github.com/django-money/django-money/issues/102
.. _#101: https://github.com/django-money/django-money/issues/101
.. _#95: https://github.com/django-money/django-money/issues/95
.. _#90: https://github.com/django-money/django-money/issues/90
.. _#86: https://github.com/django-money/django-money/issues/86
.. _#80: https://github.com/django-money/django-money/issues/80
.. _#418: https://github.com/django-money/django-money/issues/418
.. _#411: https://github.com/django-money/django-money/issues/411
.. _#519: https://github.com/django-money/django-money/issues/519
.. _#521: https://github.com/django-money/django-money/issues/521
.. _#522: https://github.com/django-money/django-money/issues/522
.. _#678: https://github.com/django-money/django-money/pull/678


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
.. _niklasb: https://github.com/niklasb
.. _nerdoc: https://github.com/nerdoc
.. _paoloxnet: https://github.com/paoloxnet
.. _pjdelport: https://github.com/pjdelport
.. _plumdog: https://github.com/plumdog
.. _rach: https://github.com/rach
.. _rapIsKal: https://github.com/rapIsKal
.. _richardowen: https://github.com/richardowen
.. _satels: https://github.com/satels
.. _sjdines: https://github.com/sjdines
.. _snbuchholz: https://github.com/snbuchholz
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
