Settings
========

The following settings are available in [djmoney/settings.py](https://github.com/django-money/django-money/blob/main/djmoney/settings.py) - documentation pull requests are welcome.

* DEFAULT_CURRENCY (documented below)
* CURRENCIES (undocumented)
* CURRENCY_CHOICES (undocumented)
* CURRENCY_DECIMAL_PLACES (undocumented)
* CURRENCY_CODE_MAX_LENGTH (undocumented)
* MONEY_FORMAT (undocumented)

Settings for currency conversion:

* OPEN_EXCHANGE_RATES_URL (undocumented)
* OPEN_EXCHANGE_RATES_APP_ID (undocumented)
* FIXER_URL (undocumented)
* FIXER_ACCESS_KEY (undocumented)
* BASE_CURRENCY (undocumented)
* EXCHANGE_BACKEND (undocumented)
* RATES_CACHE_TIMEOUT (undocumented)

DEFAULT_CURRENCY
-----------------

The `DEFAULT_CURRENCY` setting specifies the default currency used for monetary fields in your Django application. 
By default, it is set to `None`, meaning no default currency is applied unless explicitly configured.

### Configuration

You can configure the `DEFAULT_CURRENCY` in your Django project's `settings.py` file. For example:

.. code-block:: python

    DEFAULT_CURRENCY = "USD"

This will set the default currency to US Dollars.

### Usage in Fields

The `DEFAULT_CURRENCY` is used in fields like `MoneyField` to set a default currency. If not explicitly overridden, 
the field will use the globally configured `DEFAULT_CURRENCY`.

Example:

.. code-block:: python

    from djmoney.models.fields import MoneyField

    class Product(models.Model):
        price = MoneyField(max_digits=10, decimal_places=2, default_currency="EUR")

In this example, the `price` field will use Euros (`EUR`) as its currency, overriding the global `DEFAULT_CURRENCY`.

