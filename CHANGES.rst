Changes in 0.9
--------------

NB! If you are using custom model managers **not** named `objects` and you expect them to still work, please read below.

Changes and new features
^^^^^^^^^^^^^^^^^^^^^^^^

- Improved South support (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added support for ``Value`` and ``Func`` expressions in queries (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Django REST Framework support `179 <https://github.com/django-money/django-money/issues/179>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Changed auto conversion of currencies using djmoney_rates (added in 0.7.3) to
  be off by default. You must now add ``AUTO_CONVERT_MONEY = True`` in
  your ``settings.py`` if you want this feature. `199 <https://github.com/django-money/django-money/issues/199>`_  `Luke Plant <https://github.com/spookylukey>`_
- Fixed default currency value for nullable fields in forms `138 <https://github.com/django-money/django-money/issues/138>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added ``in`` lookup support (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed ``_has_changed`` deprecation warnings `206 <https://github.com/django-money/django-money/issues/206>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Django 1.10 support `198 <https://github.com/django-money/django-money/issues/198>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Only make `objects` a MoneyManager instance automatically `194 <https://github.com/django-money/django-money/issues/194>`_ and `201 <https://github.com/django-money/django-money/issues/201>`_ (`Jeongkyu Shin <https://github.com/inureyes>`_)
- Fixed ``get_or_create`` crash, when ``defaults`` is passed. `213 <https://github.com/django-money/django-money/issues/213>` (`Dmitry Dygalo <https://github.com/Stranger6667>`_, `Luke Plant <https://github.com/spookylukey>`_)

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
- Added support for serialization of ``MoneyPatched`` instances in migrations (`Alex Riina <https://github.com/AlexRiina>`_)
- Fixed fields caching `186 <https://github.com/django-money/django-money/issues/186>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed m2m fields data loss on Django < 1.8 `184 <https://github.com/django-money/django-money/issues/184>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Improved django-money-rates support `173 <https://github.com/django-money/django-money/issues/173>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed managers access via instances `86 <https://github.com/django-money/django-money/issues/86>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed currency handling behaviour `172 <https://github.com/django-money/django-money/issues/172>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Many PEP8 & flake8 fixes (`Benjamin Bach <https://github.com/benjaoming>`_)
- Added pre-commit hooks support (`Benjamin Bach <https://github.com/benjaoming>`_)
- Fixed filtration with ``F`` expressions `174 <https://github.com/django-money/django-money/issues/174>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed querying on Django 1.8+ `166 <https://github.com/django-money/django-money/issues/166>`_ (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Extended ``F`` expressions support (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added isort integration (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Refactored test suite (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Django master support (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Fixed Python 3.2 compatibility (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Makefile for common commands (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Codecov.io integration (`Dmitry Dygalo <https://github.com/Stranger6667>`_)
- Added Python 3.5 builds to tox.ini and travis.yml (`Dmitry Dygalo <https://github.com/Stranger6667>`_)

Changes in 0.7.6
----------------
- Fix for ``get_or_create`` / ``create`` manager methods not respecting currency code (`Mateusz Mikołajczyk <https://github.com/toudi>`_)
- Fix unit tests (`Mateusz Mikołajczyk <https://github.com/toudi>`_)
- Fix for using ``MoneyField`` with ``F`` expressions when using Django >= 1.8 (`Mateusz Mikołajczyk <https://github.com/toudi>`_)
- Mention Django 1.9 in tox.ini (`Benjamin Bach <https://github.com/benjaoming>`_)
- Added correct paths for py.test discovery (`Benjamin Bach <https://github.com/benjaoming>`_)

Changes in 0.7.5
----------------
- Fallback to ``_meta.fields`` if ``_meta.get_fields`` raises ``AttributeError`` `149 <https://github.com/django-money/django-money/issues/149>`_ (`Bruno Alla <https://github.com/browniebroke>`_)
- pip Instructions updated (`Ghelo Tolentino <https://github.com/GheloAce>`_)

Changes in 0.7.4
----------------
- Fixed loaddata (`Andrei Kuzmin <https://github.com/jack-cvr>`_)
- Python 2.6 fixes (`Andrei Kuzmin <https://github.com/jack-cvr>`_)
- Fixed currency choices ordering (`Antony Seedhouse <https://github.com/synotna>`_)
- Support for Django 1.9 (`Krzysztof Jagiello <https://github.com/kjagiello>`_)

Changes in 0.7.3
----------------
- Sum different currencies (`Diego Navarro <https://github.com/dnmellen>`_)
- Added ``__eq__`` method (`Benjamin Bach <https://github.com/benjaoming>`_)
- Comparison of different currencies (`Benjamin Bach <https://github.com/benjaoming>`_)
- Default currency (`Benjamin Bach <https://github.com/benjaoming>`_)
- Fix using Choices for setting currency choices (`Benjamin Bach <https://github.com/benjaoming>`_)
- Fix tests for Python 2.6 (`Andrew Plummer <https://github.com/plumdog>`_)

Changes in 0.7.2
----------------
- Better checks on ``None`` values (`tsouvarev <https://github.com/tsouvarev>`_, `Stuart Dines <https://github.com/sjdines>`_)
- Consistency with South declarations and calling ``str`` function (`Stuart Dines <https://github.com/sjdines>`_)

Changes in 0.7
--------------
- Django 1.8 compatibility (`willhcr <https://github.com/willhcr>`_)
- Fix bug in printing ``MoneyField`` (`Michael Palumbo <https://github.com/YAmikep>`_)

Changes in 0.6
--------------
- Tox cleanup (`Edwin Lunando <https://github.com/edwinlunando>`_)
- Added Python 3 trove classifier (`Jeroen Dekkers <https://github.com/dekkers>`_)
- Improved ``README`` (`Germán Larraín <https://github.com/glarrain>`_)
- Appends _currency to non-money ExpressionFields `101 <https://github.com/django-money/django-money/issues/101>`_ (`Alex Hayes <https://github.com/alexhayes>`_, `Alex Riina <https://github.com/AlexRiina>`_, `Brian Kung <https://github.com/briankung>`_)
- Data truncated for column `103 <https://github.com/django-money/django-money/issues/103>`_ (`Alex Hayes <https://github.com/alexhayes>`_)
- Proxy Model with MoneyField returns wrong class `80 <https://github.com/django-money/django-money/issues/80>`_ (`Luke Plant <https://github.com/spookylukey>`_)
- Fixed ``has_changed`` not working `95 <https://github.com/django-money/django-money/issues/95>`_ (`Luke Plant <https://github.com/spookylukey>`_)
- Added/Cleaned up tests (`Luke Plant <https://github.com/spookylukey>`_, `Alex Riina <https://github.com/AlexRiina>`_)

Changes in 0.5
--------------
- Django 1.7 compatibility (`François Rejeté <https://github.com/w00kie>`_)
- Added ``choices=`` to instantiation of currency widget (`David Stockwell <https://github.com/davidstockwell>`_)
- Nullable ``MoneyField`` should act as ``default=None`` (`Jacob Hansson <https://github.com/jakewins>`_)
- Fixed bug where a non-required ``MoneyField`` threw an exception (`Luke Plant <https://github.com/spookylukey>`_)

Changes in 0.4
--------------
- Python 3 compatibility
- Added tox tests
- Added format localization
- Added tag ``money_localize``

Changes in 0.3.3
----------------
- Fixed issues with money widget not passing attrs up to django's render method, caused id attribute to not be set in html for widgets (`Adam Bregenzer <https://github.com/adambregenzer>`_)
- Fixed issue of default currency not being passed on to widget (`snbuchholz <https://github.com/snbuchholz>`_)
- Implemented the ``south_triple_field`` to add support for South migration (`Michele Mattioni <https://github.com/mattions>`_)
- Return the right default for South (`Michele Mattioni <https://github.com/mattions>`_)
- Django 1.5 compatibility fix (`devlocal <https://github.com/devlocal>`_)

Changes in 0.3.2
----------------
- Fixed issues with ``display_for_field`` not detecting fields correctly (`Adam Bregenzer <https://github.com/adambregenzer>`_)
- Added South ignore rule to avoid duplicate currency field when using the frozen ORM (`Rach Belaid <https://github.com/rach>`_)
- Disallow override of objects manager if not setting it up with an instance (`Rach Belaid <https://github.com/rach>`_)

Changes in 0.3.1
----------------
- Fix ``AttributeError`` when Model inherit a manager (`Rach Belaid <https://github.com/rach>`_)
- Correctly serialize the field (`Anand Kumria <https://github.com/akumria>`_)

Changes in 0.3
--------------
- Allow django-money to be specified as read-only in a model (`Anand Kumria <https://github.com/akumria>`_)
- South support: Declare default attribute values. (`Piët Delport <https://github.com/pjdelport>`_)
