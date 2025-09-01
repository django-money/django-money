import django
import django.contrib.admin.utils as admin_utils
from django.urls import reverse

import pytest

from djmoney.money import Money

from .testapp.models import ModelWithParentAndCallableFields, ModelWithVanillaMoneyField, ParentModel


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


def test_admin_with_formset(admin_user, admin_client):
    """Test to assure that formsets with MoneyFields behave correctly"""

    parent = ParentModel.objects.create()
    obj = ModelWithParentAndCallableFields.objects.create(parent=parent)

    url = reverse(
        "admin:testapp_parentmodel_change",
        kwargs={
            "object_id": obj.pk,
        },
    )
    response = admin_client.get(url)
    assert response.status_code == 200

    print(response.content)

    response = admin_client.post(
        url,
        {
            "modelwithparentandcallablefields_set-TOTAL_FORMS": 2,
            "modelwithparentandcallablefields_set-INITIAL_FORMS": 1,
            "modelwithparentandcallablefields_set-MIN_NUM_FORMS": 0,
            "modelwithparentandcallablefields_set-MAX_NUM_FORMS": 2,
            # The first object exists. We sent back updated values.
            "modelwithparentandcallablefields_set-0-modelwithcallabledefaultanddefaultcurrency_ptr": obj.pk,
            "modelwithparentandcallablefields_set-0-parent": 1,
            "modelwithparentandcallablefields_set-0-money_0": 123,
            "modelwithparentandcallablefields_set-0-money_1": "CHF",
            "initial-modelwithparentandcallablefields_set-0-money": "\\xe2\\x82\\xac0.00",
            # We want this to be all default values and check that it is NOT created
            "modelwithparentandcallablefields_set-1-modelwithcallabledefaultanddefaultcurrency_ptr": "",
            "modelwithparentandcallablefields_set-1-parent": 1,
            "modelwithparentandcallablefields_set-1-money_0": "0.00",
            "modelwithparentandcallablefields_set-1-money_1": (
                "[Decimal(&#x27;0.00&#x27;), &lt;function get_default_currency at 0x7f639b897100&gt;]"
            ),
        },
    )

    assert response.status_code == 302
