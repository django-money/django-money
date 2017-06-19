# -*- coding: utf-8 -*-
import json

from django import VERSION
from django.core.management import call_command
from django.core.serializers.base import DeserializationError

import pytest

from djmoney.serializers import Deserializer, Serializer
from moneyed import Money

from .testapp.models import ModelWithDefaultAsInt


pytestmark = pytest.mark.django_db

not_django14 = pytest.mark.skipif(VERSION[:3] < (1, 5), reason="Django 1.4 doesn't support ignorenonexistent option")


if VERSION[:3] < (1, 8):
    ignore = 'ignore'
else:
    ignore = 'ignorenonexistent'


def test_m2m_fields_are_not_lost(concrete_instance, m2m_object):
    """
    See #184.
    """
    value = Serializer().serialize([concrete_instance])
    m2m_data = list(Deserializer(value, ignorenonexistent=True))[0].m2m_data
    assert m2m_object in ModelWithDefaultAsInt.objects.filter(pk__in=m2m_data['m2m_field'])


@pytest.fixture
def fixture_file(tmpdir):
    return tmpdir.join('dump.json')


def dumpdata(capsys):
    call_command('dumpdata', 'testapp')
    return capsys.readouterr()[0]


def loaddata(fixture_file, ignore_value=False):
    call_command('loaddata', str(fixture_file), **{ignore: ignore_value})


def test_dumpdata(capsys, fixture_file):
    money = Money(10, 'EUR')
    instance = ModelWithDefaultAsInt.objects.create(money=money)
    data = dumpdata(capsys)
    fixture_file.write(data)
    instance.delete()
    loaddata(fixture_file)
    assert ModelWithDefaultAsInt.objects.get().money == money


def test_load_invalid(capsys, fixture_file):
    data = '[{"model": "testapp.unknown_model", "pk": 1, "fields": {"money_currency": "USD", "money": "1.00"}}]'
    fixture_file.write(data)
    if VERSION[:2] == (1, 4):
        # In Django 1.4 exceptions are in stderr
        loaddata(fixture_file)
        assert "DeserializationError: Invalid model identifier: 'testapp.unknown_model'" in capsys.readouterr()[1]
    else:
        with pytest.raises(DeserializationError):
            loaddata(fixture_file)


@not_django14
def test_load_invalid_ignore(fixture_file):
    data = '[{"model": "testapp.unknown_model", "pk": 1, "fields": {"money_currency": "USD", "money": "1.00"}}, ' \
           '{"model": "testapp.modelwithdefaultasint", "pk": 2, "fields": {"money_currency": "USD", "money": "1.00"}}]'
    fixture_file.write(data)
    loaddata(fixture_file, True)


@not_django14
def test_old_fields_skip(capsys, fixture_file):
    money = Money(10, 'EUR')
    instance = ModelWithDefaultAsInt.objects.create(money=money)
    data = dumpdata(capsys)
    instance.delete()
    out = json.loads(data)
    out[0]['fields']['old_field'] = 1
    out = json.dumps(out)
    fixture_file.write(out)
    loaddata(fixture_file, True)
    assert ModelWithDefaultAsInt.objects.get().money == money
