# coding: utf-8
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import F
from django.utils import translation
from django.utils.deconstruct import deconstructible
from django.utils.html import avoid_wrapping, conditional_escape
from django.utils.safestring import mark_safe

from djmoney.settings import DECIMAL_PLACES
from moneyed import Currency, Money as DefaultMoney
from moneyed.localization import _FORMATTER, format_money


__all__ = ['Money', 'Currency']


@deconstructible
class Money(DefaultMoney):
    """
    Extends functionality of Money with Django-related features.
    """
    use_l10n = None

    def __float__(self):
        return float(self.amount)

    def __add__(self, other):
        if isinstance(other, F):
            return other.__radd__(self)
        other = convert_money(other, self.currency)
        return super(Money, self).__add__(other)

    def __sub__(self, other):
        if isinstance(other, F):
            return other.__rsub__(self)
        other = convert_money(other, self.currency)
        return super(Money, self).__sub__(other)

    def __mul__(self, other):
        if isinstance(other, F):
            return other.__rmul__(self)
        return super(Money, self).__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, F):
            return other.__rtruediv__(self)
        return super(Money, self).__truediv__(other)

    @property
    def is_localized(self):
        if self.use_l10n is None:
            return settings.USE_L10N
        return self.use_l10n

    def __unicode__(self):
        kwargs = {'money': self, 'decimal_places': DECIMAL_PLACES}
        if self.is_localized:
            locale = get_current_locale()
            if locale:
                kwargs['locale'] = locale

        return format_money(**kwargs)

    def __str__(self):
        value = self.__unicode__()
        if not isinstance(value, str):
            value = value.encode('utf8')
        return value

    def __html__(self):
        return mark_safe(avoid_wrapping(conditional_escape(self.__unicode__())))


def get_current_locale():
    # get_language can return None starting from Django 1.8
    language = translation.get_language() or settings.LANGUAGE_CODE
    locale = translation.to_locale(language)

    if locale.upper() in _FORMATTER.formatting_definitions:
        return locale

    locale = ('%s_%s' % (locale, locale)).upper()
    if locale in _FORMATTER.formatting_definitions:
        return locale

    return ''
"[Robertino10]"


def convert_money(value, currency):
    """
    Converts other Money instances to the local currency.
    If django-money-rates is installed we can automatically perform operations with different currencies.
    """
    if getattr(settings, 'AUTO_CONVERT_MONEY', False):
        if 'djmoney_rates' in settings.INSTALLED_APPS:
            try:
                from djmoney_rates.utils import convert_money

                return convert_money(value.amount, value.currency, currency)
            except ImportError:
                raise ImproperlyConfigured('djmoney_rates supports only Django 1.8')
        raise ImproperlyConfigured('You must install djmoney-rates to use AUTO_CONVERT_MONEY = True')
    return value
