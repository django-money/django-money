Changes in 0.9.1
----------------

- Fix packaging.

Changes in 0.9.0
----------------

NB! If you are using custom model managers **not** named `objects` and you expect them to still work, please read below.

Changes and new features
^^^^^^^^^^^^^^^^^^^^^^^^

- Improved South support (`Stranger6667`_)
- Added support for ``Value`` and ``Func`` expressions in queries (`Stranger6667`_)
- Added Django REST Framework support `#179`_ (`Stranger6667`_)
- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. `#199`_ (`spookylukey`_)
- Fixed default currency value for nullable fields in forms `#138`_ (`Stranger6667`_)
- Added ``in`` lookup support (`Stranger6667`_)
- Fixed ``_has_changed`` deprecation warnings `#206`_ (`Stranger6667`_)
- Added Django 1.10 support `#198`_ (`Stranger6667`_)
- Only make `objects` a MoneyManager instance automatically `#194`_ and `#201`_ (`inureyes`_)
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

Changes in 0.8
--------------
- Added support for serialization of ``MoneyPatched`` instances in migrations (`AlexRiina`_)
- Fixed fields caching `#186`_ (`Stranger6667`_)
- Fixed m2m fields data loss on Django < 1.8 `#184`_ (`Stranger6667`_)
- Improved django-money-rates support `#173`_ (`Stranger6667`_)
- Fixed managers access via instances `#86`_ (`Stranger6667`_)
- Fixed currency handling behaviour `#172`_ (`Stranger6667`_)
- Many PEP8 & flake8 fixes (`benjaoming`_)
- Added pre-commit hooks support (`benjaoming`_)
- Fixed filtration with ``F`` expressions `#174`_ (`Stranger6667`_)
- Fixed querying on Django 1.8+ `#166`_ (`Stranger6667`_)
- Extended ``F`` expressions support (`Stranger6667`_)
- Added isort integration (`Stranger6667`_)
- Refactored test suite (`Stranger6667`_)
- Added Django master support (`Stranger6667`_)
- Fixed Python 3.2 compatibility (`Stranger6667`_)
- Added Makefile for common commands (`Stranger6667`_)
- Added Codecov.io integration (`Stranger6667`_)
- Added Python 3.5 builds to tox.ini and travis.yml (`Stranger6667`_)

Changes in 0.7.6
----------------
- Fix for ``get_or_create`` / ``create`` manager methods not respecting currency code (`toudi`_)
- Fix unit tests (`toudi`_)
- Fix for using ``MoneyField`` with ``F`` expressions when using Django >= 1.8 (`toudi`_)
- Mention Django 1.9 in tox.ini (`benjaoming`_)
- Added correct paths for py.test discovery (`benjaoming`_)

Changes in 0.7.5
----------------
- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` `#149`_ (`browniebroke`_)
- pip Instructions updated (`GheloAce`_)

Changes in 0.7.4
----------------
- Fixed loaddata (`jack-cvr`_)
- Python 2.6 fixes (`jack-cvr`_)
- Fixed currency choices ordering (`synotna`_)
- Support for Django 1.9 (`kjagiello`_)

Changes in 0.7.3
----------------
- Sum different currencies (`dnmellen`_)
- Added ``__eq__`` method (`benjaoming`_)
- Comparison of different currencies (`benjaoming`_)
- Default currency (`benjaoming`_)
- Fix using Choices for setting currency choices (`benjaoming`_)
- Fix tests for Python 2.6 (`plumdog`_)

Changes in 0.7.2
----------------
- Better checks on ``None`` values (`tsouvarev`_, `sjdines`_)
- Consistency with South declarations and calling ``str`` function (`sjdines`_)

Changes in 0.7
--------------
- Django 1.8 compatibility (`willhcr`_)
- Fix bug in printing ``MoneyField`` (`YAmikep`_)

Changes in 0.6
--------------
- Tox cleanup (`edwinlunando`_)
- Added Python 3 trove classifier (`dekkers`_)
- Improved ``README`` (`glarrain`_)
- Appends _currency to non-money ExpressionFields `#101`_ (`alexhayes`_, `AlexRiina`_, `briankung`_)
- Data truncated for column `#103`_ (`alexhayes`_)
- Proxy Model with MoneyField returns wrong class `#80`_ (`spookylukey`_)
- Fixed ``has_changed`` not working `#95`_ (`spookylukey`_)
- Added/Cleaned up tests (`spookylukey`_, `AlexRiina`_)

Changes in 0.5
--------------
- Django 1.7 compatibility (`w00kie`_)
- Added ``choices=`` to instantiation of currency widget (`davidstockwell`_)
- Nullable ``MoneyField`` should act as ``default=None`` (`jakewins`_)
- Fixed bug where a non-required ``MoneyField`` threw an exception (`spookylukey`_)

Changes in 0.4
--------------
- Python 3 compatibility
- Added tox tests
- Added format localization
- Added tag ``money_localize``

Changes in 0.3.3
----------------
- Fixed issues with money widget not passing attrs up to django's render method, caused id attribute to not be set in html for widgets (`adambregenzer`_)
- Fixed issue of default currency not being passed on to widget (`snbuchholz`_)
- Implemented the ``south_triple_field`` to add support for South migration (`mattions`_)
- Return the right default for South (`mattions`_)
- Django 1.5 compatibility fix (`devlocal`_)

Changes in 0.3.2
----------------
- Fixed issues with ``display_for_field`` not detecting fields correctly (`adambregenzer`_)
- Added South ignore rule to avoid duplicate currency field when using the frozen ORM (`rach`_)
- Disallow override of objects manager if not setting it up with an instance (`rach`_)

Changes in 0.3.1
----------------
- Fix ``AttributeError`` when Model inherit a manager (`rach`_)
- Correctly serialize the field (`akumria`_)

Changes in 0.3
--------------
- Allow django-money to be specified as read-only in a model (`akumria`_)
- South support: Declare default attribute values. (`pjdelport`_)


.. _#213: https://github.com/django-money/django-money/issues/213
.. _#206: https://github.com/django-money/django-money/issues/206
.. _#201: https://github.com/django-money/django-money/issues/201
.. _#199: https://github.com/django-money/django-money/issues/199
.. _#198: https://github.com/django-money/django-money/issues/198
.. _#194: https://github.com/django-money/django-money/issues/194
.. _#186: https://github.com/django-money/django-money/issues/186
.. _#184: https://github.com/django-money/django-money/issues/184
.. _#179: https://github.com/django-money/django-money/issues/179
.. _#174: https://github.com/django-money/django-money/issues/174
.. _#173: https://github.com/django-money/django-money/issues/173
.. _#172: https://github.com/django-money/django-money/issues/172
.. _#166: https://github.com/django-money/django-money/issues/166
.. _#149: https://github.com/django-money/django-money/issues/149
.. _#138: https://github.com/django-money/django-money/issues/138
.. _#103: https://github.com/django-money/django-money/issues/103
.. _#101: https://github.com/django-money/django-money/issues/101
.. _#95: https://github.com/django-money/django-money/issues/95
.. _#86: https://github.com/django-money/django-money/issues/86
.. _#80: https://github.com/django-money/django-money/issues/80

.. _AlexRiina: https://github.com/AlexRiina
.. _GheloAce: https://github.com/GheloAce
.. _Stranger6667: https://github.com/Stranger6667
.. _YAmikep: https://github.com/YAmikep
.. _adambregenzer: https://github.com/adambregenzer
.. _akumria: https://github.com/akumria
.. _alexhayes: https://github.com/alexhayes
.. _benjaoming: https://github.com/benjaoming
.. _briankung: https://github.com/briankung
.. _browniebroke: https://github.com/browniebroke
.. _davidstockwell: https://github.com/davidstockwell
.. _dekkers: https://github.com/dekkers
.. _devlocal: https://github.com/devlocal
.. _dnmellen: https://github.com/dnmellen
.. _edwinlunando: https://github.com/edwinlunando
.. _glarrain: https://github.com/glarrain
.. _inureyes: https://github.com/inureyes
.. _jack-cvr: https://github.com/jack-cvr
.. _jakewins: https://github.com/jakewins
.. _kjagiello: https://github.com/kjagiello
.. _mattions: https://github.com/mattions
.. _pjdelport: https://github.com/pjdelport
.. _plumdog: https://github.com/plumdog
.. _rach: https://github.com/rach
.. _sjdines: https://github.com/sjdines
.. _snbuchholz: https://github.com/snbuchholz
.. _spookylukey: https://github.com/spookylukey
.. _synotna: https://github.com/synotna
.. _toudi: https://github.com/toudi
.. _tsouvarev: https://github.com/tsouvarev
.. _w00kie: https://github.com/w00kie
.. _willhcr: https://github.com/willhcr