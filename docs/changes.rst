Changelog
=========


`3.6b2`_ - 2025-09-01
---------------------

**Added**

- Support for callable ``default`` and ``currency_default``, and ``currency_choices`` :github-issue:`683` (:github-user:`benjaoming`)
- Add ``backend`` kwarg to ``convert_money`` function :github-issue:`787` (:github-user:`heckad`)

**Fixed**

- The auto-generated hidden input field that tracks initial data in formsets with MoneyField should now work :github-issue:`803` (:github-user:`benjaoming`)

**Changed**

- Migrate to pyproject.toml and uv :github-issue:`791` (:github-user:`browniebroke`)


`3.5.4`_ - 2025-04-17
---------------------

**Added**

- Django 5.2 and Python 3.13 support :github-issue:`785` (:github-user:`gvangool` and :github-user:`browniebroke`)


`3.5.3`_ - 2024-08-01
---------------------

**Fixed**

- django-rest-framework: MoneyField does not work anymore with custom serializer fields :github-issue:`768` (:github-user:`apjama`)

**Added**

- Django 5.1 support :github-issue:`767` (:github-user:`benjaoming`)


`3.5.2`_ - 2024-05-07
---------------------

**Fixed**

- django-rest-framework: Fix regression from 3.5 :github-issue:`762` (:github-user:`dariusmazeika`)


`3.5.1`_ - 2024-05-05
---------------------

**Fixed**

- django-rest-framework: Fix regression from 3.5 :github-issue:`757` (:github-user:`phillipuniverse`)
- Add `base` parameter to openexchangerates.org backend :github-issue:`751` (:github-user:`foarsitter`)

`3.5`_ - 2024-05-04
-------------------

.. important::

   If you generated ``MoneyField`` migrations in the previous series 3.4.x, you may have to manually edit subsequent migrations. Please share your successful approaches in :github-issue:`731`.


**Fixed**

- Revert 3.4 patch, meaning that auto-generated CurrencyField is once again part of migrations :github-issue:`731` (:github-user:`benjaoming`)
- django-rest-framework: MinMoneyValidator and MaxMoneyValidator fixed, may require default_currency defined :github-issue:`722` (:github-user:`hosamhamdy258` :github-user:`errietta` :github-user:`benjaoming`)

**Added**

- Django 5.0 support :github-issue:`753` (:github-user:`benjaoming`)

**Removed**

- Official support for Django 2.2, 3.2, 4.0, 4.1 :github-issue:`753` (:github-user:`benjaoming`)


`3.4.1`_ - 2023-11-30
---------------------

**Fixed**

- The default setting for ``CURRENCY_CHOICES`` excluded the currency choice defined by ``DEFAULT_CURRENCY``. :github-issue:`739` (:github-user:`Naggafin`)


`3.4`_ - 2023-10-17
-------------------

.. note::

   If you are using Django REST Framework or any other mechanism that relies on a custom serializer,
   please note that you now manually have to register the serializer.
   See :ref:`this code snippet <index:Note on serialization>`.

**Changed**

- Don't register Django Money serializers by default, instead the user should actively register a serializer in the ``settings.py`` :github-issue:`636` (:github-user:`emorozov`)


`3.3`_ - 2023-09-10
-------------------

**Fixed**

- Fix detection of necessary migrations. Note that this means that previously undetected migrations will be detected as of this version  :github-issue:`725` (:github-user:`vanschelven`)

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

- Python 3.11 support :github-issue:`700` (:github-user:`sdarmofal`)
- Django 4.2 support :github-issue:`700` (:github-user:`sdarmofal`)
- Pyright support for .pyi files :github-issue:`686` (:github-user:`karolyi`)
- Support for ``Coalesce`` :github-issue:`678` (:github-user:`stianjensen`)

**Fixed**

- Support for ``Money`` type with ``Coalesce`` in ``QuerySet.update()`` :github-issue:`678` (:github-user:`stianjensen`)
- pre-commit config for moved flake8 repo (:github-user:`sdarmofal`)
- Use latest setup-python GitHub Action :github-issue:`692` (:github-user:`sondrelg`)
- Optimize: Rate is always 1 if source and target are equal :github-issue:`689` (:github-user:`nschlemm`)
- Fixer.io backend: Avoid 403 errors :github-issue:`681` (:github-user:`spaut33`)

`3.0`_ - 2022-06-20
--------------------

**Changed**
- Update py-moneyed to 2.0. :github-issue:`638` (:github-user:`antonagestam`, :github-user:`flaeppe`, :github-user:`paoloxnet`)
- Remove the deprecated ``Money.decimal_places_display`` property and argument. :github-issue:`638` (:github-user:`antonagestam`, :github-user:`flaeppe`, :github-user:`paoloxnet`)
- Remove the deprecated ``CURRENCY_DECIMAL_PLACES_DISPLAY`` setting. :github-issue:`638` (:github-user:`antonagestam`, :github-user:`flaeppe`, :github-user:`paoloxnet`)
- Null constraint on an implicit ``CurrencyField`` is now declared from ``null=...`` argument to ``MoneyField``. :github-issue:`638` (:github-user:`antonagestam`, :github-user:`flaeppe`, :github-user:`paoloxnet`)

**Fixed**

- Improve the internal check for whether a currency is provided :github-issue:`657` (:github-user:`davidszotten`)
- Fix test suite for django main branch :github-issue:`657` (:github-user:`davidszotten`)
- ``MoneyField`` raises ``TypeError`` when default contains a valid amount but no currence, i.e. ``Money(123, None)``. :github-issue:`661` (:github-user:`flaeppe`)
- ``MoneyField`` supports default of type ``bytes`` :github-issue:`661` (:github-user:`flaeppe`)

**Added**

- Add support for Django 4.0 and 4.1.
- Add support for Python 3.10.

**Removed**

- Drop support for Django 3.1.
- Drop support for Python 3.6.


`2.1.1`_ - 2022-01-02
---------------------

**Changed**

- Renamed ``master`` branch to ``main`` (:github-user:`benjaoming`)

**Fixed**

- Make Django REST Framework integration always raise lower-level errors as ``ValidationError``. :github-issue:`601`, :github-issue:`637` (:github-user:`flaeppe`)
- False positives in Migration changes, improvements to ``MoneyField.deconstruct``. :github-issue:`646`, :github-issue:`648` (:github-user:`flaeppe`)

`2.1`_ - 2021-09-17
-------------------

**Added**

- Add support for Django 3.2. :github-issue:`612` (:github-user:`antonagestam`)

**Removed**

- Drop support for Django 1.11, 2.1 and 3.0. :github-issue:`612` (:github-user:`antonagestam`)
- Drop support for Python 3.5. :github-issue:`612` (:github-user:`antonagestam`)

`2.0.3`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour when non-``Money`` instances are involved. :github-issue:`630` (:github-user:`tned73`)

`2.0.2`_ - 2021-09-04
---------------------

**Fixed**

- Inconsistent ``Money._copy_attributes`` behaviour. :github-issue:`629` (:github-user:`tned73`)

`2.0.1`_ - 2021-07-09
---------------------

**Fixed**

- Invalid deprecation warning behavior. :github-issue:`624` (:github-user:`nerdoc`)

`2.0`_ - 2021-05-23
-------------------

**Added**

- New setting ``CURRENCY_CODE_MAX_LENGTH`` configures default max_length for MoneyField and ``exchange`` app models.

**Changed**

- BREAKING: Update ``py-moneyed`` to ``>=1.2,<2``. It uses ``babel`` to format ``Money``, which formats it differently than ``py-moneyed<1``. :github-issue:`567` (:github-user:`antonagestam`)

**Deprecated**

- ``Money.decimal_places_display`` will be removed in django-money 3.0.
- ``CURRENCY_DECIMAL_PLACES_DISPLAY`` will be removed in django-money 3.0.

`1.3.1`_ - 2021-02-04
---------------------

**Fixed**

- Do not mutate the input ``moneyed.Money`` class to ``djmoney.money.Money`` in ``MoneyField.default`` and F-expressions. :github-issue:`603` (:github-user:`moser`)

`1.3`_ - 2021-01-10
-------------------

**Added**

- Improved localization: New setting ``CURRENCY_DECIMAL_PLACES_DISPLAY`` configures decimal places to display for each configured currency. :github-issue:`521` (:github-user:`wearebasti`)

**Changed**

- Set the default value for ``models.fields.MoneyField`` to ``NOT_PROVIDED``. (:github-user:`tned73`)

**Fixed**

- Pin ``pymoneyed<1.0`` as it changed the ``repr`` output of the ``Money`` class. (:github-user:`Stranger6667`)
- Subtracting ``Money`` from ``moneyed.Money``. Regression, introduced in ``1.2``. :github-issue:`593` (:github-user:`Stranger6667`)
- Missing the right ``Money.decimal_places`` and ``Money.decimal_places_display`` values after some arithmetic operations. :github-issue:`595` (:github-user:`Stranger6667`)

`1.2.2`_ - 2020-12-29
---------------------

**Fixed**

- Confusing "number-over-money" division behavior by backporting changes from ``py-moneyed``. :github-issue:`586` (:github-user:`wearebasti`)
- ``AttributeError`` when a ``Money`` instance is divided by ``Money``. :github-issue:`585` (:github-user:`niklasb`)

`1.2.1`_ - 2020-11-29
---------------------

**Fixed**

- Aggregation through a proxy model. :github-issue:`583` (:github-user:`tned73`)

`1.2`_ - 2020-11-26
-------------------

**Fixed**

- Resulting Money object from arithmetics (add / sub / ...) inherits maximum decimal_places from arguments :github-issue:`522` (:github-user:`wearebasti`)
- ``DeprecationWarning`` related to the usage of ``cafile`` in ``urlopen``. :github-issue:`553` (:github-user:`Stranger6667`)

**Added**

- Django 3.1 support

`1.1`_ - 2020-04-06
-------------------

**Fixed**

- Optimize money operations on MoneyField instances with the same currencies. :github-issue:`541` (:github-user:`horpto`)

**Added**

- Support for ``Money`` type in ``QuerySet.bulk_update()`` :github-issue:`534` (:github-user:`satels`)

`1.0`_ - 2019-11-08
-------------------

**Added**

- Support for money descriptor customization. (:github-user:`Stranger6667`)
- Fix ``order_by()`` not returning money-compatible queryset :github-issue:`519` (:github-user:`lieryan`)
- Django 3.0 support

**Removed**

- Support for Django 1.8 & 2.0. (:github-user:`Stranger6667`)
- Support for Python 2.7. :github-issue:`515` (:github-user:`benjaoming`)
- Support for Python 3.4. (:github-user:`Stranger6667`)
- ``MoneyPatched``, use ``djmoney.money.Money`` instead. (:github-user:`Stranger6667`)

**Fixed**

- Support instances with ``decimal_places=0`` :github-issue:`509` (:github-user:`fara`)

`0.15.1`_ - 2019-06-22
----------------------

**Fixed**

- Respect field ``decimal_places`` when instantiating ``Money`` object from field db values. :github-issue:`501` (:github-user:`astutejoe`)
- Restored linting in CI tests (:github-user:`benjaoming`)

`0.15`_ - 2019-05-30
--------------------

.. warning:: This release contains backwards incompatibility, please read the release notes below.

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Remove implicit default value on non-nullable MoneyFields.
  Backwards incompatible change: set explicit ``default=0.0`` to keep previous behavior. :github-issue:`411` (:github-user:`washeck`)
- Remove support for calling ``float`` on ``Money`` instances. Use the ``amount`` attribute instead. (:github-user:`Stranger6667`)
- ``MinMoneyValidator`` and ``MaxMoneyValidator`` are not inherited from Django's ``MinValueValidator`` and ``MaxValueValidator`` anymore. :github-issue:`376`
- In model and non-model forms ``forms.MoneyField`` uses ``CURRENCY_DECIMAL_PLACES`` as the default value for ``decimal_places``. :github-issue:`434` (:github-user:`Stranger6667`, :github-user:`andytwoods`)

**Added**

- Add ``Money.decimal_places`` for per-instance configuration of decimal places in the string representation.
- Support for customization of ``CurrencyField`` length. Some cryptocurrencies could have codes longer than three characters. :github-issue:`480` (:github-user:`Stranger6667`, :github-user:`MrFus10n`)
- Add ``default_currency`` option for REST Framework field. :github-issue:`475` (:github-user:`butorov`)

**Fixed**

- Failing certificates checks when accessing 3rd party exchange rates backends.
  Fixed by adding `certifi` to the dependencies list. :github-issue:`403` (:github-user:`Stranger6667`)
- Fixed model-level ``validators`` behavior in REST Framework. :github-issue:`376` (:github-user:`rapIsKal`, :github-user:`Stranger6667`)
- Setting keyword argument ``default_currency=None`` for ``MoneyField`` did not revert to ``settings.DEFAULT_CURRENCY`` and set ``str(None)`` as database value for currency. :github-issue:`490`  (:github-user:`benjaoming`)

**Changed**

- Allow using patched ``django.core.serializers.python._get_model`` in serializers, which could be helpful for
  migrations. (:github-user:`Formulka`, :github-user:`Stranger6667`)

`0.14.4`_ - 2019-01-07
----------------------

**Changed**

- Re-raise arbitrary exceptions in JSON deserializer as `DeserializationError`. (:github-user:`Stranger6667`)

**Fixed**

- Invalid Django 1.8 version check in ``djmoney.models.fields.MoneyField.value_to_string``. (:github-user:`Stranger6667`)
- InvalidOperation in ``djmoney.contrib.django_rest_framework.fields.MoneyField.get_value`` when amount is None and currency is not None. :github-issue:`458` (:github-user:`carvincarl`)

`0.14.3`_ - 2018-08-14
----------------------

**Fixed**

- ``djmoney.forms.widgets.MoneyWidget`` decompression on Django 2.1+. :github-issue:`443` (:github-user:`Stranger6667`)

`0.14.2`_ - 2018-07-23
----------------------

**Fixed**

- Validation of ``djmoney.forms.fields.MoneyField`` when ``disabled=True`` is passed to it. :github-issue:`439` (:github-user:`stinovlas`, :github-user:`Stranger6667`)

`0.14.1`_ - 2018-07-17
----------------------

**Added**

- Support for indirect rates conversion through maximum 1 extra step (when there is no direct conversion rate:
  converting by means of a third currency for which both source and target currency have conversion
  rates). :github-issue:`425` (:github-user:`Stranger6667`, :github-user:`77cc33`)

**Fixed**

- Error was raised when trying to do a query with a `ModelWithNullableCurrency`. :github-issue:`427` (:github-user:`Woile`)

`0.14`_ - 2018-06-09
--------------------

**Added**

- Caching of exchange rates. :github-issue:`398` (:github-user:`Stranger6667`)
- Added support for nullable ``CurrencyField``. :github-issue:`260` (:github-user:`Stranger6667`)

**Fixed**

- Same currency conversion getting MissingRate exception :github-issue:`418` (:github-user:`humrochagf`)
- `TypeError` during templatetag usage inside a for loop on Django 2.0. :github-issue:`402` (:github-user:`f213`)

**Removed**

- Support for Python 3.3 :github-issue:`410` (:github-user:`benjaoming`)
- Deprecated ``choices`` argument from ``djmoney.forms.fields.MoneyField``. Use ``currency_choices`` instead. (:github-user:`Stranger6667`)

`0.13.5`_ - 2018-05-19
----------------------

**Fixed**

- Missing in dist, ``djmoney/__init__.py``. :github-issue:`417` (:github-user:`benjaoming`)

`0.13.4`_ - 2018-05-19
----------------------

**Fixed**

- Packaging of ``djmoney.contrib.exchange.management.commands``. :github-issue:`412` (:github-user:`77cc33`, :github-user:`Stranger6667`)

`0.13.3`_ - 2018-05-12
----------------------

**Added**

- Rounding support via ``round`` built-in function on Python 3. (:github-user:`Stranger6667`)

`0.13.2`_ - 2018-04-16
----------------------

**Added**

- Django Admin integration for exchange rates. :github-issue:`392` (:github-user:`Stranger6667`)

**Fixed**

- Exchange rates. TypeError when decoding JSON on Python 3.3-3.5. :github-issue:`399` (:github-user:`kcyeu`)
- Managers patching for models with custom ``Meta.default_manager_name``. :github-issue:`400` (:github-user:`Stranger6667`)

`0.13.1`_ - 2018-04-07
----------------------

**Fixed**

- Regression: Could not run w/o ``django.contrib.exchange`` :github-issue:`388` (:github-user:`Stranger6667`)

`0.13`_ - 2018-04-07
--------------------

**Added**

- Currency exchange :github-issue:`385` (:github-user:`Stranger6667`)

**Removed**

- Support for ``django-money-rates`` :github-issue:`385` (:github-user:`Stranger6667`)
- Deprecated ``Money.__float__`` which is implicitly called on some ``sum()`` operations :github-issue:`347`. (:github-user:`jonashaag`)

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

- Fixed ``BaseMoneyValidator`` with falsy limit values. :github-issue:`371` (:github-user:`1337`)

`0.12.2`_ - 2017-12-12
----------------------

**Fixed**

- Django master branch compatibility. :github-issue:`361` (:github-user:`Stranger6667`)
- Fixed ``get_or_create`` for models with shared currency. :github-issue:`364` (:github-user:`Stranger6667`)

**Changed**

- Removed confusing rounding to integral value in ``Money.__repr__``. :github-issue:`366` (:github-user:`Stranger6667`, :github-user:`evenicoulddoit`)

`0.12.1`_ - 2017-11-20
----------------------

**Fixed**

- Fixed migrations on SQLite. :github-issue:`139`, :github-issue:`338` (:github-user:`Stranger6667`)
- Fixed ``Field.rel.to`` usage for Django 2.0. :github-issue:`349` (:github-user:`richardowen`)
- Fixed Django REST Framework behaviour for serializers without ``*_currency`` field in serializer's ``Meta.fields``. :github-issue:`351` (:github-user:`elcolie`, :github-user:`Stranger6667`)

`0.12`_ - 2017-10-22
--------------------

**Added**

- Ability to specify name for currency field. :github-issue:`195` (:github-user:`Stranger6667`)
- Validators for ``MoneyField``. :github-issue:`308` (:github-user:`Stranger6667`)

**Changed**

- Improved ``Money`` support. Now ``django-money`` fully relies on ``pymoneyed`` localization everywhere, including Django admin. :github-issue:`276` (:github-user:`Stranger6667`)
- Implement ``__html__`` method. If used in Django templates, an ``Money`` object's amount and currency are now separated with non-breaking space (``&nbsp;``) :github-issue:`337` (:github-user:`jonashaag`)

**Deprecated**

- ``djmoney.models.fields.MoneyPatched`` and ``moneyed.Money`` are deprecated. Use ``djmoney.money.Money`` instead.

**Fixed**

- Fixed model field validation. :github-issue:`308` (:github-user:`Stranger6667`).
- Fixed managers caching for Django >= 1.10. :github-issue:`318` (:github-user:`Stranger6667`).
- Fixed ``F`` expressions support for ``in`` lookups. :github-issue:`321` (:github-user:`Stranger6667`).
- Fixed money comprehension on querysets. :github-issue:`331` (:github-user:`Stranger6667`, :github-user:`jaavii1988`).
- Fixed errors in Django Admin integration. :github-issue:`334` (:github-user:`Stranger6667`, :github-user:`adi-`).

**Removed**

- Dropped support for Python 2.6 and 3.2. (:github-user:`Stranger6667`)
- Dropped support for Django 1.4, 1.5, 1.6, 1.7 and 1.9. (:github-user:`Stranger6667`)

`0.11.4`_ - 2017-06-26
----------------------

**Fixed**

- Fixed money parameters processing in update queries. :github-issue:`309` (:github-user:`Stranger6667`)

`0.11.3`_ - 2017-06-19
----------------------

**Fixed**

- Restored support for Django 1.4, 1.5, 1.6, and 1.7 & Python 2.6 :github-issue:`304` (:github-user:`Stranger6667`)

`0.11.2`_ - 2017-05-31
----------------------

**Fixed**

- Fixed field lookup regression. :github-issue:`300` (:github-user:`lmdsp`, :github-user:`Stranger6667`)

`0.11.1`_ - 2017-05-26
----------------------

**Fixed**

- Fixed access to models properties. :github-issue:`297` (:github-user:`mithrilstar`, :github-user:`Stranger6667`)

**Removed**

- Dropped support for Python 2.6. (:github-user:`Stranger6667`)
- Dropped support for Django < 1.8. (:github-user:`Stranger6667`)

`0.11`_ - 2017-05-19
--------------------

**Added**

- An ability to set custom currency choices via ``CURRENCY_CHOICES`` settings option. :github-issue:`211` (:github-user:`Stranger6667`, :github-user:`ChessSpider`)

**Fixed**

- Fixed ``AttributeError`` in ``get_or_create`` when the model have no default. :github-issue:`268` (:github-user:`Stranger6667`, :github-user:`lobziik`)
- Fixed ``UnicodeEncodeError`` in string representation of ``MoneyPatched`` on Python 2. :github-issue:`272` (:github-user:`Stranger6667`)
- Fixed various displaying errors in Django Admin . :github-issue:`232`, :github-issue:`220`, :github-issue:`196`, :github-issue:`102`, :github-issue:`90` (:github-user:`Stranger6667`,
  :github-user:`arthurk`, :github-user:`mstarostik`, :github-user:`eriktelepovsky`, :github-user:`jplehmann`, :github-user:`graik`, :github-user:`benjaoming`, :github-user:`k8n`, :github-user:`yellow-sky`)
- Fixed non-Money values support for ``in`` lookup. :github-issue:`278` (:github-user:`Stranger6667`)
- Fixed available lookups with removing of needless lookup check. :github-issue:`277` (:github-user:`Stranger6667`)
- Fixed compatibility with ``py-moneyed``. (:github-user:`Stranger6667`)
- Fixed ignored currency value in Django REST Framework integration. :github-issue:`292` (:github-user:`gonzalobf`)

`0.10.2`_ - 2017-02-18
----------------------

**Added**

- Added ability to configure decimal places output. :github-issue:`154`, :github-issue:`251` (:github-user:`ivanchenkodmitry`)

**Fixed**

- Fixed handling of ``defaults`` keyword argument in ``get_or_create`` method. :github-issue:`257` (:github-user:`kjagiello`)
- Fixed handling of currency fields lookups in ``get_or_create`` method. :github-issue:`258` (:github-user:`Stranger6667`)
- Fixed ``PendingDeprecationWarning`` during form initialization. :github-issue:`262` (:github-user:`Stranger6667`, :github-user:`spookylukey`)
- Fixed handling of ``F`` expressions which involve non-Money fields. :github-issue:`265` (:github-user:`Stranger6667`)

`0.10.1`_ - 2016-12-26
----------------------

**Fixed**

- Fixed default value for ``djmoney.forms.fields.MoneyField``. :github-issue:`249` (:github-user:`tsouvarev`)

`0.10`_ - 2016-12-19
--------------------

**Changed**

- Do not fail comparisons because of different currency. Just return ``False`` :github-issue:`225` (:github-user:`benjaoming` and :github-user:`ivirabyan`)

**Fixed**

- Fixed ``understands_money`` behaviour. Now it can be used as a decorator :github-issue:`215` (:github-user:`Stranger6667`)
- Fixed: Not possible to revert MoneyField currency back to default :github-issue:`221` (:github-user:`benjaoming`)
- Fixed invalid ``creation_counter`` handling. :github-issue:`235` (:github-user:`msgre` and :github-user:`Stranger6667`)
- Fixed broken field resolving. :github-issue:`241` (:github-user:`Stranger6667`)

`0.9.1`_ - 2016-08-01
---------------------

**Fixed**

- Fixed packaging.

`0.9.0`_ - 2016-07-31
---------------------

NB! If you are using custom model managers **not** named ``objects`` and you expect them to still work, please read below.

**Added**

- Support for ``Value`` and ``Func`` expressions in queries. (:github-user:`Stranger6667`)
- Support for ``in`` lookup. (:github-user:`Stranger6667`)
- Django REST Framework support. :github-issue:`179` (:github-user:`Stranger6667`)
- Django 1.10 support. :github-issue:`198` (:github-user:`Stranger6667`)
- Improved South support. (:github-user:`Stranger6667`)

**Changed**

- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. :github-issue:`199` (:github-user:`spookylukey`)
- Only make ``objects`` a MoneyManager instance automatically. :github-issue:`194` and :github-issue:`201` (:github-user:`inureyes`)

**Fixed**

- Fixed default currency value for nullable fields in forms. :github-issue:`138` (:github-user:`Stranger6667`)
- Fixed ``_has_changed`` deprecation warnings. :github-issue:`206` (:github-user:`Stranger6667`)
- Fixed ``get_or_create`` crash, when ``defaults`` is passed. :github-issue:`213` (:github-user:`Stranger6667`, :github-user:`spookylukey`)

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

- Support for serialization of ``MoneyPatched`` instances in migrations. (:github-user:`AlexRiina`)
- Improved django-money-rates support. :github-issue:`173` (:github-user:`Stranger6667`)
- Extended ``F`` expressions support. (:github-user:`Stranger6667`)
- Pre-commit hooks support. (:github-user:`benjaoming`)
- Isort integration. (:github-user:`Stranger6667`)
- Makefile for common commands. (:github-user:`Stranger6667`)
- Codecov.io integration. (:github-user:`Stranger6667`)
- Python 3.5 builds to tox.ini and travis.yml. (:github-user:`Stranger6667`)
- Django master support. (:github-user:`Stranger6667`)
- Python 3.2 compatibility. (:github-user:`Stranger6667`)

**Changed**

- Refactored test suite (:github-user:`Stranger6667`)

**Fixed**

- Fixed fields caching. :github-issue:`186` (:github-user:`Stranger6667`)
- Fixed m2m fields data loss on Django < 1.8. :github-issue:`184` (:github-user:`Stranger6667`)
- Fixed managers access via instances. :github-issue:`86` (:github-user:`Stranger6667`)
- Fixed currency handling behaviour. :github-issue:`172` (:github-user:`Stranger6667`)
- Many PEP8 & flake8 fixes. (:github-user:`benjaoming`)
- Fixed filtration with ``F`` expressions. :github-issue:`174` (:github-user:`Stranger6667`)
- Fixed querying on Django 1.8+. :github-issue:`166` (:github-user:`Stranger6667`)

`0.7.6`_ - 2016-01-08
---------------------

**Added**

- Added correct paths for py.test discovery. (:github-user:`benjaoming`)
- Mention Django 1.9 in tox.ini. (:github-user:`benjaoming`)

**Fixed**

- Fix for ``get_or_create`` / ``create`` manager methods not respecting currency code. (:github-user:`toudi`)
- Fix unit tests. (:github-user:`toudi`)
- Fix for using ``MoneyField`` with ``F`` expressions when using Django >= 1.8. (:github-user:`toudi`)

`0.7.5`_ - 2015-12-22
---------------------

**Fixed**

- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` :github-issue:`149` (:github-user:`browniebroke`)
- pip instructions updated. (:github-user:`GheloAce`)

`0.7.4`_ - 2015-11-02
---------------------

**Added**

- Support for Django 1.9 (:github-user:`kjagiello`)

**Fixed**

- Fixed loaddata. (:github-user:`jack-cvr`)
- Python 2.6 fixes. (:github-user:`jack-cvr`)
- Fixed currency choices ordering. (:github-user:`synotna`)

`0.7.3`_ - 2015-10-16
---------------------

**Added**

- Sum different currencies. (:github-user:`dnmellen`)
- ``__eq__`` method. (:github-user:`benjaoming`)
- Comparison of different currencies. (:github-user:`benjaoming`)
- Default currency. (:github-user:`benjaoming`)

**Fixed**

- Fix using Choices for setting currency choices. (:github-user:`benjaoming`)
- Fix tests for Python 2.6. (:github-user:`plumdog`)

`0.7.2`_ - 2015-09-01
---------------------

**Fixed**

- Better checks on ``None`` values. (:github-user:`tsouvarev`, :github-user:`sjdines`)
- Consistency with South declarations and calling ``str`` function. (:github-user:`sjdines`)

`0.7.1`_ - 2015-08-11
---------------------

**Fixed**

- Fix bug in printing ``MoneyField``. (:github-user:`YAmikep`)
- Added fallback value for current locale getter. (:github-user:`sjdines`)

`0.7.0`_ - 2015-06-14
---------------------

**Added**

- Django 1.8 compatibility. (:github-user:`willhcr`)

`0.6.0`_ - 2015-05-23
---------------------

**Added**

- Python 3 trove classifier. (:github-user:`dekkers`)

**Changed**

- Tox cleanup. (:github-user:`edwinlunando`)
- Improved ``README``. (:github-user:`glarrain`)
- Added/Cleaned up tests. (:github-user:`spookylukey`, :github-user:`AlexRiina`)

**Fixed**

- Append ``_currency`` to non-money ExpressionFields. :github-issue:`101` (:github-user:`alexhayes`, :github-user:`AlexRiina`, :github-user:`briankung`)
- Data truncated for column. :github-issue:`103` (:github-user:`alexhayes`)
- Fixed ``has_changed`` not working. :github-issue:`95` (:github-user:`spookylukey`)
- Fixed proxy model with ``MoneyField`` returns wrong class. :github-issue:`80` (:github-user:`spookylukey`)

`0.5.0`_ - 2014-12-15
---------------------

**Added**

- Django 1.7 compatibility. (:github-user:`w00kie`)

**Fixed**

- Added ``choices=`` to instantiation of currency widget. (:github-user:`davidstockwell`)
- Nullable ``MoneyField`` should act as ``default=None``. (:github-user:`jakewins`)
- Fixed bug where a non-required ``MoneyField`` threw an exception. (:github-user:`spookylukey`)

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

- South support via implementing the ``south_triple_field`` method. (:github-user:`mattions`)

**Fixed**

- Fixed issues with money widget not passing attrs up to django's render method, caused id attribute to not be set in html for widgets. (:github-user:`adambregenzer`)
- Fixed issue of default currency not being passed on to widget. (:github-user:`snbuchholz`)
- Return the right default for South. (:github-user:`mattions`)
- Django 1.5 compatibility. (:github-user:`devlocal`)

`0.3.2`_ - 2012-11-30
---------------------

**Fixed**

- Fixed issues with ``display_for_field`` not detecting fields correctly. (:github-user:`adambregenzer`)
- Added South ignore rule to avoid duplicate currency field when using the frozen ORM. (:github-user:`rach`)
- Disallow override of objects manager if not setting it up with an instance. (:github-user:`rach`)

`0.3.1`_ - 2012-10-11
---------------------

**Fixed**

- Fix ``AttributeError`` when Model inherit a manager. (:github-user:`rach`)
- Correctly serialize the field. (:github-user:`akumria`)

`0.3`_ - 2012-09-30
-------------------

**Added**

- Allow django-money to be specified as read-only in a model. (:github-user:`akumria`)
- South support: Declare default attribute values. (:github-user:`pjdelport`)

`0.2`_ - 2012-04-10
-------------------

- Initial public release

.. _3.6b2: https:///github.com/django-money/django-money/compare/3.5.4...HEAD
.. _3.5.4: https:///github.com/django-money/django-money/compare/3.5.4...3.5.3
.. _3.5.3: https:///github.com/django-money/django-money/compare/3.5.3...3.5.2
.. _3.5.2: https:///github.com/django-money/django-money/compare/3.5.2...3.5.1
.. _3.5.1: https:///github.com/django-money/django-money/compare/3.5.1...3.5
.. _3.5: https:///github.com/django-money/django-money/compare/3.5...3.4.1
.. _3.4.1: https:///github.com/django-money/django-money/compare/3.4...3.4.1
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
