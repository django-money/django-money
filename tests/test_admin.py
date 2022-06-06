import django
import django.contrib.admin.utils as admin_utils

import pytest

from djmoney.money import Money

from .testapp.models import ModelWithVanillaMoneyField


MONEY_FIELD = ModelWithVanillaMoneyField._meta.get_field("money")
INTEGER_FIELD = ModelWithVanillaMoneyField._meta.get_field("integer")


@pytest.mark.parametrize(
    "value, expected",
    (
        (Money(10, "RUB"), "10,00\xa0RUB"),  # Issue 232
        (Money(1000, "SAR"), "1\xa0000,00\xa0SAR"),  # Issue 196
        (Money(1000, "PLN"), "1\xa0000,00\xa0PLN"),  # Issue 102
        (Money("3.33", "EUR"), "3,33\xa0€"),  # Issue 90
    ),
)
def test_display_for_field(settings, value, expected):
    # This now defaults to True and raises RemovedInDjango50Warning
    if django.VERSION < (4, 0):
        settings.USE_L10N = True
    # This locale has no definitions in py-moneyed, so it will work for localized money representation.
    settings.LANGUAGE_CODE = "cs"
    assert admin_utils.display_for_field(value, MONEY_FIELD, "") == expected


def test_default_display():
    assert admin_utils.display_for_field(10, INTEGER_FIELD, "") == "10"
