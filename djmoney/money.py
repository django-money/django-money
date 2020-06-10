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

    def _fix_decimal_places(self, *args):
        """ Make sure to user 'biggest' number of decimal places of all given money instances """
        candidates = (getattr(candidate, "decimal_places", 0) for candidate in args)
        return max([self.decimal_places, *candidates])

    def __add__(self, other):
        if isinstance(other, F):
            return other.__radd__(self)
        other = maybe_convert(other, self.currency)
        result = super().__add__(other)
        result.decimal_places = self._fix_decimal_places(other)
        return result

    def __sub__(self, other):
        if isinstance(other, F):
            return other.__rsub__(self)
        other = maybe_convert(other, self.currency)
        result = super().__sub__(other)
        result.decimal_places = self._fix_decimal_places(other)
        return result

    def __mul__(self, other):
        if isinstance(other, F):
            return other.__rmul__(self)
        result = super().__mul__(other)
        result.decimal_places = self._fix_decimal_places(other)
        return result

    def __truediv__(self, other):
        if isinstance(other, F):
            return other.__rtruediv__(self)
        result = super().__truediv__(other)
        result.decimal_places = self._fix_decimal_places(other)
        return result

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

    # DefaultMoney sets those synonym functions
    # we overwrite the 'targets' so the wrong synonyms are called
    # Example: we overwrite __add__; __radd__ calls __add__ on DefaultMoney...
    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rtruediv__ = __truediv__


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
