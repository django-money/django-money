import json
from unittest.mock import patch

from django.core.management import call_command
from django.core.serializers.base import DeserializationError

import pytest

from djmoney.money import Money
from djmoney.serializers import Deserializer, Serializer

from .testapp.models import ModelWithDefaultAsInt, ModelWithSharedCurrency


pytestmark = pytest.mark.django_db


def test_m2m_fields_are_not_lost(concrete_instance, m2m_object):
    """
    See #184.
    """
    value = Serializer().serialize([concrete_instance])
    m2m_data = list(Deserializer(value, ignorenonexistent=True))[0].m2m_data
    assert m2m_object in ModelWithDefaultAsInt.objects.filter(pk__in=m2m_data["m2m_field"])


@pytest.fixture
def fixture_file(tmpdir):
    return tmpdir.join("dump.json")


def dumpdata(capsys):
    call_command("dumpdata", "testapp")
    return capsys.readouterr()[0]


def loaddata(fixture_file, ignore_value=False):
    call_command("loaddata", str(fixture_file), ignorenonexistent=ignore_value)


def test_dumpdata(capsys, fixture_file):
    money = Money(10, "EUR")
    instance = ModelWithDefaultAsInt.objects.create(money=money)
    data = dumpdata(capsys)
    fixture_file.write(data)
    instance.delete()
    loaddata(fixture_file)
    assert ModelWithDefaultAsInt.objects.get().money == money


def test_load_invalid(fixture_file):
    data = '[{"model": "testapp.unknown_model", "pk": 1, "fields": {"money_currency": "USD", "money": "1.00"}}]'
    fixture_file.write(data)
    with pytest.raises(DeserializationError):
        loaddata(fixture_file)


def test_load_invalid_ignore(fixture_file):
    data = (
        '[{"model": "testapp.unknown_model", "pk": 1, "fields": {"money_currency": "USD", "money": "1.00"}}, '
        '{"model": "testapp.modelwithdefaultasint", "pk": 2, "fields": {"money_currency": "USD", "money": "1.00"}}]'
    )
    fixture_file.write(data)
    loaddata(fixture_file, True)


def test_old_fields_skip(capsys, fixture_file):
    money = Money(10, "EUR")
    instance = ModelWithDefaultAsInt.objects.create(money=money)
    data = dumpdata(capsys)
    instance.delete()
    out = json.loads(data)
    out[0]["fields"]["old_field"] = 1
    out = json.dumps(out)
    fixture_file.write(out)
    loaddata(fixture_file, True)
    assert ModelWithDefaultAsInt.objects.get().money == money


def test_deserialization_error():
    with pytest.raises(DeserializationError):
        list(Deserializer("invalid JSON"))


def test_patched_get_model(fixture_file):
    """Sometimes it is useful to patch `django.code.serializers.python._get_model`.

    Our code should use the patched version."""
    data = '[{"model": "testapp.unknown_model", "pk": 1, "fields": {"money_currency": "USD", "money": "1.00"}}]'
    fixture_file.write(data)

    def _get_model(identifier):
        return ModelWithDefaultAsInt

    with patch("django.core.serializers.python._get_model", _get_model):
        loaddata(fixture_file)
    assert ModelWithDefaultAsInt.objects.get().money == Money(1, "USD")


def test_serialize_currency_field(fixture_file):
    data = """[
    {
        "model": "testapp.modelwithsharedcurrency",
        "pk": 1,
        "fields": {"first": "1.00", "second": "2.00", "currency": "USD"}
    }
]"""
    fixture_file.write(data)
    loaddata(fixture_file)
    assert ModelWithSharedCurrency.objects.get().first == Money(1, "USD")
