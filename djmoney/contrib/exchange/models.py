from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string

from djmoney.settings import EXCHANGE_BACKEND

from .exceptions import MissingRate


class ExchangeBackend(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    last_update = models.DateTimeField(auto_now=True)
    base_currency = models.CharField(max_length=3)

    def __str__(self):
        return self.name

    def clear_rates(self):
        self.rates.all().delete()


class Rate(models.Model):
    currency = models.CharField(max_length=3)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    backend = models.ForeignKey(ExchangeBackend, on_delete=models.CASCADE, related_name='rates')

    class Meta:
        unique_together = (('currency', 'backend'), )


def get_default_backend_name():
    return import_string(EXCHANGE_BACKEND).name


def get_one():
    """
    For SQLite it is required to cast value to NUMERIC type, otherwise integer division will be used.
    """
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        return '1::NUMERIC'
    return 1


def get_rate(source, target, backend=None):
    """
    Returns an exchange rate between source and target currencies.
    Converts exchange rate on the DB side if there is no backends with given base currency.
    Uses data from the default backend if the backend is not specified.
    """
    if backend is None:
        backend = get_default_backend_name()
    if source == target:
        return 1
    try:
        forward = models.Q(currency=target, backend__base_currency=source)
        reverse = models.Q(currency=source, backend__base_currency=target)
        return Rate.objects.annotate(
            rate=models.Case(
                models.When(forward, then=models.F('value')),
                models.When(reverse, then=models.Value(get_one()) / models.F('value')),
            )
        ).get(forward | reverse, backend=backend).rate
    except Rate.DoesNotExist:
        raise MissingRate('Rate %s -> %s does not exist' % (source, target))


def convert_money(value, currency):
    if 'djmoney.contrib.exchange' not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured(
            "You have to add 'djmoney.contrib.exchange' to INSTALLED_APPS in order to use currency exchange"
        )
    amount = value.amount * get_rate(value.currency, currency)
    return value.__class__(amount, currency)
