# coding: utf-8
import pytest

from djmoney.serializers import Deserializer, Serializer

from .testapp.models import ModelWithDefaultAsInt


pytestmark = pytest.mark.django_db


def test_m2m_fields_are_not_lost(concrete_instance, m2m_object):
    """
    See #184.
    """
    value = Serializer().serialize([concrete_instance])
    m2m_data = list(Deserializer(value, ignorenonexistent=True))[0].m2m_data
    assert m2m_object in ModelWithDefaultAsInt.objects.filter(pk__in=m2m_data['m2m_field'])
