.. _changes:

Changelog
=========

`Unreleased`_
-------------

`0.12.3`_ - 2017-12-13
----------------------

Fixed
~~~~~

- Fixed `BaseMoneyValidator` with falsy limit values. `#371`_ (`1337`_)

`0.12.2`_ - 2017-12-12
----------------------

Fixed
~~~~~

- Django master branch compatibility. `#361`_ (`Stranger6667`_)
- Fixed ``get_or_create`` for models with shared currency. `#364`_ (`Stranger6667`_)

Changed
~~~~~~~
- Removed confusing rounding to integral value in ``Money.__repr__``. `#366`_ (`Stranger6667`_, `evenicoulddoit`_)

`0.12.1`_ - 2017-11-20
----------------------

Fixed
~~~~~

- Fixed migrations on SQLite. `#139`_, `#338`_ (`Stranger6667`_)
- Fixed ``Field.rel.to`` usage for Django 2.0. `#349`_ (`richardowen`_)
- Fixed Django REST Framework behaviour for serializers without `*_currency` field in serializer's ``Meta.fields``. `#351`_ (`elcolie`_, `Stranger6667`_)

`0.12`_ - 2017-10-22
--------------------

Added
~~~~~

- Ability to specify name for currency field. `#195`_ (`Stranger6667`_)
- Validators for ``MoneyField``. `#308`_ (`Stranger6667`_)

Changed
~~~~~~~
- Improved ``Money`` support. Now ``django-money`` fully relies on ``pymoneyed`` localization everywhere, including Django admin. `#276`_ (`Stranger6667`_)
- Implement ``__html__`` method. If used in Django templates, an ``Money`` object's amount and currency are now separated with non-breaking space (``&nbsp;``) `#337`_ (`jonashaag`_)

Deprecated
~~~~~~~~~~
- ``djmoney.models.fields.MoneyPatched`` and ``moneyed.Money`` are deprecated. Use ``djmoney.money.Money`` instead.

Fixed
~~~~~

- Fixed model field validation. `#308`_ (`Stranger6667`_).
- Fixed managers caching for Django >= 1.10. `#318`_ (`Stranger6667`_).
- Fixed ``F`` expressions support for ``in`` lookups. `#321`_ (`Stranger6667`_).
- Fixed money comprehension on querysets. `#331`_ (`Stranger6667`_, `jaavii1988`_).
- Fixed errors in Django Admin integration. `#334`_ (`Stranger6667`_, `adi-`_).

Removed
~~~~~~~
- Dropped support for Python 2.6 and 3.2. (`Stranger6667`_)
- Dropped support for Django 1.4, 1.5, 1.6, 1.7 and 1.9. (`Stranger6667`_)

`0.11.4`_ - 2017-06-26
----------------------

Fixed
~~~~~
- Fixed money parameters processing in update queries. `#309`_ (`Stranger6667`_)

`0.11.3`_ - 2017-06-19
----------------------

Fixed
~~~~~
- Restored support for Django 1.4, 1.5, 1.6, and 1.7 & Python 2.6 `#304`_ (`Stranger6667`_)

`0.11.2`_ - 2017-05-31
----------------------

Fixed
~~~~~
- Fixed field lookup regression. `#300`_ (`lmdsp`_, `Stranger6667`_)

`0.11.1`_ - 2017-05-26
----------------------

Fixed
~~~~~
- Fixed access to models properties. `#297`_ (`mithrilstar`_, `Stranger6667`_)

Removed
~~~~~~~
- Dropped support for Python 2.6. (`Stranger6667`_)
- Dropped support for Django < 1.8. (`Stranger6667`_)

`0.11`_ - 2017-05-19
--------------------

Added
~~~~~
- An ability to set custom currency choices via ``CURRENCY_CHOICES`` settings option. `#211`_ (`Stranger6667`_, `ChessSpider`_)

Fixed
~~~~~
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

Added
~~~~~
- Added ability to configure decimal places output. `#154`_, `#251`_ (`ivanchenkodmitry`_)

Fixed
~~~~~
- Fixed handling of ``defaults`` keyword argument in ``get_or_create`` method. `#257`_ (`kjagiello`_)
- Fixed handling of currency fields lookups in ``get_or_create`` method. `#258`_ (`Stranger6667`_)
- Fixed ``PendingDeprecationWarning`` during form initialization. `#262`_ (`Stranger6667`_, `spookylukey`_)
- Fixed handling of ``F`` expressions which involve non-Money fields. `#265`_ (`Stranger6667`_)

`0.10.1`_ - 2016-12-26
----------------------

Fixed
~~~~~
- Fixed default value for ``djmoney.forms.fields.MoneyField``. `#249`_ (`tsouvarev`_)

`0.10`_ - 2016-12-19
--------------------

Changed
~~~~~~~
- Do not fail comparisons because of different currency. Just return ``False`` `#225`_ (`benjaoming`_ and `ivirabyan`_)

Fixed
~~~~~
- Fixed ``understands_money`` behaviour. Now it can be used as a decorator `#215`_ (`Stranger6667`_)
- Fixed: Not possible to revert MoneyField currency back to default `#221`_ (`benjaoming`_)
- Fixed invalid ``creation_counter`` handling. `#235`_ (`msgre`_ and `Stranger6667`_)
- Fixed broken field resolving. `#241`_ (`Stranger6667`_)

`0.9.1`_ - 2016-08-01
---------------------

Fixed
~~~~~
- Fixed packaging.

`0.9.0`_ - 2016-07-31
---------------------

NB! If you are using custom model managers **not** named `objects` and you expect them to still work, please read below.

Added
~~~~~
- Support for ``Value`` and ``Func`` expressions in queries. (`Stranger6667`_)
- Support for ``in`` lookup. (`Stranger6667`_)
- Django REST Framework support. `#179`_ (`Stranger6667`_)
- Django 1.10 support. `#198`_ (`Stranger6667`_)
- Improved South support. (`Stranger6667`_)

Changed
~~~~~~~
- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. `#199`_ (`spookylukey`_)
- Only make `objects` a MoneyManager instance automatically. `#194`_ and `#201`_ (`inureyes`_)

Fixed
~~~~~
- Fixed default currency value for nullable fields in forms. `#138`_ (`Stranger6667`_)
- Fixed ``_has_changed`` deprecation warnings. `#206`_ (`Stranger6667`_)
- Fixed ``get_or_create`` crash, when ``defaults`` is passed. `#213`_ (`Stranger6667`_, `spookylukey`_)

Note about automatic model manager patches
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Added
~~~~~
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

Changed
~~~~~~~
- Refactored test suite (`Stranger6667`_)

Fixed
~~~~~
- Fixed fields caching. `#186`_ (`Stranger6667`_)
- Fixed m2m fields data loss on Django < 1.8. `#184`_ (`Stranger6667`_)
- Fixed managers access via instances. `#86`_ (`Stranger6667`_)
- Fixed currency handling behaviour. `#172`_ (`Stranger6667`_)
- Many PEP8 & flake8 fixes. (`benjaoming`_)
- Fixed filtration with ``F`` expressions. `#174`_ (`Stranger6667`_)
- Fixed querying on Django 1.8+. `#166`_ (`Stranger6667`_)

`0.7.6`_ - 2016-01-08
---------------------

Added
~~~~~
- Added correct paths for py.test discovery. (`benjaoming`_)
- Mention Django 1.9 in tox.ini. (`benjaoming`_)

Fixed
~~~~~
- Fix for ``get_or_create`` / ``create`` manager methods not respecting currency code. (`toudi`_)
- Fix unit tests. (`toudi`_)
- Fix for using ``MoneyField`` with ``F`` expressions when using Django >= 1.8. (`toudi`_)

`0.7.5`_ - 2015-12-22
---------------------

Fixed
~~~~~
- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` `#149`_ (`browniebroke`_)
- pip instructions updated. (`GheloAce`_)

`0.7.4`_ - 2015-11-02
---------------------

Added
~~~~~
- Support for Django 1.9 (`kjagiello`_)

Fixed
~~~~~
- Fixed loaddata. (`jack-cvr`_)
- Python 2.6 fixes. (`jack-cvr`_)
- Fixed currency choices ordering. (`synotna`_)

`0.7.3`_ - 2015-10-16
---------------------

Added
~~~~~
- Sum different currencies. (`dnmellen`_)
- ``__eq__`` method. (`benjaoming`_)
- Comparison of different currencies. (`benjaoming`_)
- Default currency. (`benjaoming`_)

Fixed
~~~~~
- Fix using Choices for setting currency choices. (`benjaoming`_)
- Fix tests for Python 2.6. (`plumdog`_)

`0.7.2`_ - 2015-09-01
---------------------

Fixed
~~~~~
- Better checks on ``None`` values. (`tsouvarev`_, `sjdines`_)
- Consistency with South declarations and calling ``str`` function. (`sjdines`_)

`0.7.1`_ - 2015-08-11
---------------------

Fixed
~~~~~
- Fix bug in printing ``MoneyField``. (`YAmikep`_)
- Added fallback value for current locale getter. (`sjdines`_)

`0.7.0`_ - 2015-06-14
---------------------

Added
~~~~~
- Django 1.8 compatibility. (`willhcr`_)

`0.6.0`_ - 2015-05-23
---------------------

Added
~~~~~
- Python 3 trove classifier. (`dekkers`_)

Changed
~~~~~~~
- Tox cleanup. (`edwinlunando`_)
- Improved ``README``. (`glarrain`_)
- Added/Cleaned up tests. (`spookylukey`_, `AlexRiina`_)

Fixed
~~~~~
- Append ``_currency`` to non-money ExpressionFields. `#101`_ (`alexhayes`_, `AlexRiina`_, `briankung`_)
- Data truncated for column. `#103`_ (`alexhayes`_)
- Fixed ``has_changed`` not working. `#95`_ (`spookylukey`_)
- Fixed proxy model with ``MoneyField`` returns wrong class. `#80`_ (`spookylukey`_)

`0.5.0`_ - 2014-12-15
---------------------

Added
~~~~~
- Django 1.7 compatibility. (`w00kie`_)

Fixed
~~~~~
- Added ``choices=`` to instantiation of currency widget. (`davidstockwell`_)
- Nullable ``MoneyField`` should act as ``default=None``. (`jakewins`_)
- Fixed bug where a non-required ``MoneyField`` threw an exception. (`spookylukey`_)

`0.4.2`_ - 2014-07-31
---------------------
`0.4.1`_ - 2013-11-28
---------------------
`0.4.0.0`_ - 2013-11-26
-----------------------

Added
~~~~~
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

Added
~~~~~
- South support via implementing the ``south_triple_field`` method. (`mattions`_)

Fixed
~~~~~
- Fixed issues with money widget not passing attrs up to django's render method, caused id attribute to not be set in html for widgets. (`adambregenzer`_)
- Fixed issue of default currency not being passed on to widget. (`snbuchholz`_)
- Return the right default for South. (`mattions`_)
- Django 1.5 compatibility. (`devlocal`_)

`0.3.2`_ - 2012-11-30
---------------------

Fixed
~~~~~
- Fixed issues with ``display_for_field`` not detecting fields correctly. (`adambregenzer`_)
- Added South ignore rule to avoid duplicate currency field when using the frozen ORM. (`rach`_)
- Disallow override of objects manager if not setting it up with an instance. (`rach`_)

`0.3.1`_ - 2012-10-11
---------------------

Fixed
~~~~~
- Fix ``AttributeError`` when Model inherit a manager. (`rach`_)
- Correctly serialize the field. (`akumria`_)

`0.3`_ - 2012-09-30
-------------------

Added
~~~~~
- Allow django-money to be specified as read-only in a model. (`akumria`_)
- South support: Declare default attribute values. (`pjdelport`_)

`0.2`_ - 2012-04-10
-------------------

- Initial public release

.. _Unreleased: https://github.com/django-money/django-money/compare/0.12.3...HEAD
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

.. _AlexRiina: https://github.com/AlexRiina
.. _ChessSpider: https://github.com/ChessSpider
.. _GheloAce: https://github.com/GheloAce
.. _Stranger6667: https://github.com/Stranger6667
.. _YAmikep: https://github.com/YAmikep
.. _adambregenzer: https://github.com/adambregenzer
.. _adi-: https://github.com/adi-
.. _akumria: https://github.com/akumria
.. _alexhayes: https://github.com/alexhayes
.. _arthurk: https://github.com/arthurk
.. _benjaoming: https://github.com/benjaoming
.. _briankung: https://github.com/briankung
.. _browniebroke: https://github.com/browniebroke
.. _davidstockwell: https://github.com/davidstockwell
.. _dekkers: https://github.com/dekkers
.. _devlocal: https://github.com/devlocal
.. _dnmellen: https://github.com/dnmellen
.. _edwinlunando: https://github.com/edwinlunando
.. _elcolie: https://github.com/elcolie
.. _eriktelepovsky: https://github.com/eriktelepovsky
.. _evenicoulddoit: https://github.com/evenicoulddoit
.. _glarrain: https://github.com/glarrain
.. _graik: https://github.com/graik
.. _gonzalobf: https://github.com/gonzalobf
.. _inureyes: https://github.com/inureyes
.. _ivanchenkodmitry: https://github.com/ivanchenkodmitry
.. _jaavii1988: https://github.com/jaavii1988
.. _jack-cvr: https://github.com/jack-cvr
.. _jakewins: https://github.com/jakewins
.. _jonashaag: https://github.com/jonashaag
.. _jplehmann: https://github.com/jplehmann
.. _kjagiello: https://github.com/kjagiello
.. _ivirabyan: https://github.com/ivirabyan
.. _k8n: https://github.com/k8n
.. _lmdsp: https://github.com/lmdsp
.. _lobziik: https://github.com/lobziik
.. _mattions: https://github.com/mattions
.. _mithrilstar: https://github.com/mithrilstar
.. _msgre: https://github.com/msgre
.. _mstarostik: https://github.com/mstarostik
.. _pjdelport: https://github.com/pjdelport
.. _plumdog: https://github.com/plumdog
.. _rach: https://github.com/rach
.. _richardowen: https://github.com/richardowen
.. _sjdines: https://github.com/sjdines
.. _snbuchholz: https://github.com/snbuchholz
.. _spookylukey: https://github.com/spookylukey
.. _synotna: https://github.com/synotna
.. _toudi: https://github.com/toudi
.. _tsouvarev: https://github.com/tsouvarev
.. _yellow-sky: https://github.com/yellow-sky
.. _w00kie: https://github.com/w00kie
.. _willhcr: https://github.com/willhcr
.. _1337: https://github.com/1337
