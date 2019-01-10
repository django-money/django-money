# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from djmoney.money import Money

from ..testapp.models import ModelWithVanillaMoneyField, NullMoneyFieldModel


pytestmark = pytest.mark.django_db
serializers = pytest.importorskip('rest_framework.serializers')
fields = pytest.importorskip('rest_framework.fields')


class TestMoneyField:

    def get_serializer(self, model_class, instance=None, data=fields.empty, fields_='__all__'):

        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = model_class
                fields = fields_

        return Serializer(instance=instance, data=data)

    @pytest.mark.parametrize(
        'model_class, create_kwargs, expected', (
            (NullMoneyFieldModel, {'field': None}, {'field': None, 'field_currency': 'USD'}),
            (
                NullMoneyFieldModel,
                {'field': Money(10, 'USD')},
                {'field': '10.00', 'field_currency': 'USD'}
            ),
            (
                ModelWithVanillaMoneyField,
                {'money': Money(10, 'USD')},
                {
                    'integer': 0,
                    'money': '10.00',
                    'money_currency': 'USD',
                    'second_money': '0.00',
                    'second_money_currency': 'EUR'}
            ),
        )
    )
    def test_to_representation(self, model_class, create_kwargs, expected):
        instance = model_class.objects.create(**create_kwargs)
        expected['id'] = instance.id
        serializer = self.get_serializer(model_class, instance=instance)
        assert serializer.data == expected

    @pytest.mark.parametrize(
        'model_class, field, value, expected', (
            (NullMoneyFieldModel, 'field', None, None),
            (NullMoneyFieldModel, 'field', Money(10, 'USD'), Money(10, 'USD')),
            (ModelWithVanillaMoneyField, 'money', Money(10, 'USD'), Money(10, 'USD')),
            (ModelWithVanillaMoneyField, 'money', 10, Money(10, 'XYZ')),
        )
    )
    def test_to_internal_value(self, model_class, field, value, expected):
        serializer = self.get_serializer(model_class, data={field: value})
        assert serializer.is_valid()
        instance = serializer.save()
        assert getattr(instance, field) == expected

    def test_invalid_value(self):
        serializer = self.get_serializer(ModelWithVanillaMoneyField, data={'money': None})
        assert not serializer.is_valid()
        error_text = 'This field may not be null.'
        assert serializer.errors == {'money': [error_text]}

    @pytest.mark.parametrize(
        'body, expected', (
            ({'field': '10', 'field_currency': 'EUR'}, Money(10, 'EUR')),
            ({'field': '12.20', 'field_currency': 'GBP'}, Money(12.20, 'GBP')),
            ({'field': '15.15', 'field_currency': 'USD'}, Money(15.15, 'USD')),
            ({'field': None, 'field_currency': None}, None),
            ({'field': '16', 'field_currency': None}, Decimal('16.00')),
            ({'field': None, 'field_currency': 'USD'}, None),
        ),
    )
    def test_post_put_values(self, body, expected):
        serializer = self.get_serializer(NullMoneyFieldModel, data=body)
        serializer.is_valid()
        assert serializer.validated_data['field'] == expected

    def test_serializer_with_fields(self):
        serializer = self.get_serializer(ModelWithVanillaMoneyField, data={'money': '10.00'}, fields_=('money', ))
        serializer.is_valid(True)
        assert serializer.data == {'money': '10.00'}
