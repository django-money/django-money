Settings
========

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

### Notes

- If `DEFAULT_CURRENCY` is not set in `settings.py`, it defaults to `None`.
- You can override the default currency for specific fields by using the `default_currency` argument.
