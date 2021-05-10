import warnings
from functools import partial
from types import MappingProxyType

from django.conf import settings
from django.db.models import F
from django.utils import translation
from django.utils.deconstruct import deconstructible
from django.utils.html import avoid_wrapping, conditional_escape
from django.utils.safestring import mark_safe

import moneyed.l10n
import moneyed.localization
from moneyed import Currency, Money as DefaultMoney

from .settings import DECIMAL_PLACES, DECIMAL_PLACES_DISPLAY, IS_DECIMAL_PLACES_DISPLAY_SET, MONEY_FORMAT


__all__ = ["Money", "Currency"]

_warn_decimal_places_display_deprecated = partial(
    warnings.warn,
    "`Money.decimal_places_display` is deprecated and will be removed in django-money 3.0.",
    DeprecationWarning,
)


@deconstructible
class Money(DefaultMoney):
    """
    Extends functionality of Money with Django-related features.
    """

    use_l10n = None

    def __init__(self, *args, decimal_places_display=None, format_options=None, **kwargs):
        self.decimal_places = kwargs.pop("decimal_places", DECIMAL_PLACES)
        self._decimal_places_display = decimal_places_display
        if decimal_places_display is not None:
            _warn_decimal_places_display_deprecated()
        self.format_options = MappingProxyType(format_options) if format_options is not None else None
        super().__init__(*args, **kwargs)

    @property
    def decimal_places_display(self):
        _warn_decimal_places_display_deprecated()
        if self._decimal_places_display is None:
            return DECIMAL_PLACES_DISPLAY.get(self.currency.code, self.decimal_places)
        return self._decimal_places_display

    @decimal_places_display.setter
    def decimal_places_display(self, value):
        """ Set number of digits being displayed - `None` resets to `DECIMAL_PLACES_DISPLAY` setting """
        _warn_decimal_places_display_deprecated()
        self._decimal_places_display = value

    def _copy_attributes(self, source, target):
        """Copy attributes to the new `Money` instance.

        This class stores extra bits of information about string formatting that the parent class doesn't have.
        The problem is that the parent class creates new instances of `Money` without in some of its methods and
        it does so without knowing about `django-money`-level attributes.
        For this reason, when this class uses some methods of the parent class that have this behavior, the resulting
        instances lose those attribute values.

        When it comes to what number of decimal places to choose, we take the maximum number.
        """
        for attribute_name in ("decimal_places", "decimal_places_display"):
            value = max([getattr(candidate, attribute_name, 0) for candidate in (self, source)])
            setattr(target, attribute_name, value)

    def __add__(self, other):
        if isinstance(other, F):
            return other.__radd__(self)
        other = maybe_convert(other, self.currency)
        result = super().__add__(other)
        self._copy_attributes(other, result)
        return result

    def __sub__(self, other):
        if isinstance(other, F):
            return other.__rsub__(self)
        other = maybe_convert(other, self.currency)
        result = super().__sub__(other)
        self._copy_attributes(other, result)
        return result

    def __mul__(self, other):
        if isinstance(other, F):
            return other.__rmul__(self)
        result = super().__mul__(other)
        self._copy_attributes(other, result)
        return result

    def __truediv__(self, other):
        if isinstance(other, F):
            return other.__rtruediv__(self)
        result = super().__truediv__(other)
        if isinstance(result, self.__class__):
            self._copy_attributes(other, result)
        return result

    def __rtruediv__(self, other):
        # Backported from py-moneyed, non released bug-fix
        # https://github.com/py-moneyed/py-moneyed/blob/c518745dd9d7902781409daec1a05699799474dd/moneyed/classes.py#L217-L218
        raise TypeError("Cannot divide non-Money by a Money instance.")

    @property
    def is_localized(self):
        if self.use_l10n is None:
            return settings.USE_L10N
        return self.use_l10n

    def __str__(self):
        if self._decimal_places_display is not None or IS_DECIMAL_PLACES_DISPLAY_SET:
            kwargs = {"money": self, "decimal_places": self.decimal_places_display}
            if self.is_localized:
                locale = get_current_locale(for_babel=False)
                if locale:
                    kwargs["locale"] = locale
            return moneyed.localization.format_money(**kwargs)
        format_options = {
            **MONEY_FORMAT,
            **(self.format_options or {}),
        }
        locale = get_current_locale()
        if locale:
            format_options["locale"] = locale
        return moneyed.l10n.format_money(self, **format_options)

    def __html__(self):
        return mark_safe(avoid_wrapping(conditional_escape(str(self))))

    def __round__(self, n=None):
        amount = round(self.amount, n)
        new = self.__class__(amount, self.currency)
        self._copy_attributes(self, new)
        return new

    def round(self, ndigits=0):
        new = super().round(ndigits)
        self._copy_attributes(self, new)
        return new

    def __pos__(self):
        new = super().__pos__()
        self._copy_attributes(self, new)
        return new

    def __neg__(self):
        new = super().__neg__()
        self._copy_attributes(self, new)
        return new

    def __abs__(self):
        new = super().__abs__()
        self._copy_attributes(self, new)
        return new

    def __rmod__(self, other):
        new = super().__rmod__(other)
        self._copy_attributes(self, new)
        return new

    # DefaultMoney sets those synonym functions
    # we overwrite the 'targets' so the wrong synonyms are called
    # Example: we overwrite __add__; __radd__ calls __add__ on DefaultMoney...
    __radd__ = __add__
    __rmul__ = __mul__


def get_current_locale(for_babel=True):
    # get_language can return None starting from Django 1.8
    language = translation.get_language() or settings.LANGUAGE_CODE
    locale = translation.to_locale(language)

    if for_babel:
        return locale

    if locale.upper() in moneyed.localization._FORMATTER.formatting_definitions:
        return locale

    locale = ("{}_{}".format(locale, locale)).upper()
    if locale in moneyed.localization._FORMATTER.formatting_definitions:
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
