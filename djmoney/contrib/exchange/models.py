from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string

from djmoney._compat import text_type
from djmoney.settings import EXCHANGE_BACKEND, RATES_CACHE_TIMEOUT

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


def get_rate(source, target, backend=None):
    """
    Returns an exchange rate between source and target currencies.
    Converts exchange rate on the DB side if there is no backends with given base currency.
    Uses data from the default backend if the backend is not specified.
    """
    if backend is None:
        backend = get_default_backend_name()
    key = 'djmoney:get_rate:%s:%s:%s' % (source, target, backend)
    result = cache.get(key)
    if result is not None:
        return result
    result = _get_rate(source, target, backend)
    cache.set(key, result, RATES_CACHE_TIMEOUT)
    return result


def _get_rate(source, target, backend):
    if text_type(source) == text_type(target):
        return 1
    rates = Rate.objects.filter(currency__in=(source, target), backend=backend)
    if not rates:
        raise MissingRate('Rate %s -> %s does not exist' % (source, target))
    # Direct rate
    if len(rates) == 1:
        rate = rates[0]
        if text_type(rate.currency) == text_type(target):
            return rate.value
        return 1 / rate.value
    # Indirect rate
    first, second = rates
    if text_type(first.currency) == text_type(target):
        first, second = second, first
    return second.value / first.value


def convert_money(value, currency):
    if 'djmoney.contrib.exchange' not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured(
            "You have to add 'djmoney.contrib.exchange' to INSTALLED_APPS in order to use currency exchange"
        )
    amount = value.amount * get_rate(value.currency, currency)
    return value.__class__(amount, currency)
