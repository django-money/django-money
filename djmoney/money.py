from django.conf import settings
from django.db.models import F
from django.utils import translation
from django.utils.deconstruct import deconstructible
from django.utils.html import avoid_wrapping, conditional_escape
from django.utils.safestring import mark_safe

from moneyed import Currency, Money as DefaultMoney
from moneyed.localization import _FORMATTER, format_money

from .settings import DECIMAL_PLACES


__all__ = ["Money", "Currency"]


@deconstructible
class Money(DefaultMoney):
    """
    Extends functionality of Money with Django-related features.
    """

    use_l10n = None

    def __init__(self, *args, **kwargs):
        self.decimal_places = kwargs.pop("decimal_places", DECIMAL_PLACES)
        super().__init__(*args, **kwargs)

    def __add__(self, other):
        if isinstance(other, F):
            return other.__radd__(self)
        other = maybe_convert(other, self.currency)
        return super().__add__(other)

    def __sub__(self, other):
        if isinstance(other, F):
            return other.__rsub__(self)
        other = maybe_convert(other, self.currency)
        return super().__sub__(other)

    def __mul__(self, other):
        if isinstance(other, F):
            return other.__rmul__(self)
        return super().__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, F):
            return other.__rtruediv__(self)
        return super().__truediv__(other)

    @property
    def is_localized(self):
        if self.use_l10n is None:
            return settings.USE_L10N
        return self.use_l10n

    def __str__(self):
        kwargs = {"money": self, "decimal_places": self.decimal_places}
        if self.is_localized:
            locale = get_current_locale()
            if locale:
                kwargs["locale"] = locale

        return format_money(**kwargs)

    def __html__(self):
        return mark_safe(avoid_wrapping(conditional_escape(str(self))))

    def __round__(self, n=None):
        amount = round(self.amount, n)
        return self.__class__(amount, self.currency)


def get_current_locale():
    # get_language can return None starting from Django 1.8
    language = translation.get_language() or settings.LANGUAGE_CODE
    locale = translation.to_locale(language)

    if locale.upper() in _FORMATTER.formatting_definitions:
        return locale

    locale = ("%s_%s" % (locale, locale)).upper()
    if locale in _FORMATTER.formatting_definitions:
        return locale

    return ""


def maybe_convert(value, currency):
    """
    Converts other Money instances to the local currency if `AUTO_CONVERT_MONEY` is set to True.
    """
    if getattr(settings, "AUTO_CONVERT_MONEY", False) and value.currency != currency:
        from .contrib.exchange.models import convert_money

        return convert_money(value, currency)
    return value
