# -*- coding: utf-8 -*-
import pytest

from moneyed import Money

from ..testapp.models import ModelWithVanillaMoneyField, NullMoneyFieldModel


try:
    from rest_framework import serializers
    from djmoney.contrib.django_rest_framework.helpers import IS_DRF_3
except ImportError:
    pytest.skip()


pytestmark = pytest.mark.django_db


class TestMoneyField:

    if IS_DRF_3:
        from rest_framework.fields import empty
    else:
        empty = None

    def get_serializer(self, model_class, instance=None, data=empty):

        if IS_DRF_3:
            class Serializer(serializers.ModelSerializer):
                class Meta:
                    model = model_class
                    fields = '__all__'
        else:
            class Serializer(serializers.ModelSerializer):
                class Meta:
                    model = model_class

        return Serializer(instance=instance, data=data)

    @pytest.mark.parametrize(
        'model_class, create_kwargs, expected', (
            (NullMoneyFieldModel, {'field': None}, {'field': None, 'field_currency': 'USD'}),
            (
                NullMoneyFieldModel,
                {'field': Money(10, 'USD')},
                {'field': '10.00' if IS_DRF_3 else 10, 'field_currency': 'USD'}
            ),
            (
                ModelWithVanillaMoneyField,
                {'money': Money(10, 'USD')},
                {
                    'integer': 0,
                    'money': '10.00' if IS_DRF_3 else 10,
                    'money_currency': 'USD',
                    'second_money': '0.00' if IS_DRF_3 else 0,
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
        error_text = 'This field may not be null.' if IS_DRF_3 else 'This field is required.'
        assert serializer.errors == {'money': [error_text]}

    @pytest.mark.parametrize(
        'body, expected', (
            ({'field': '10', 'field_currency': 'EUR'}, Money(10, 'EUR')),
            ({'field': '12.20', 'field_currency': 'GBP'}, Money(12.20, 'GBP')),
            ({'field': '15.15', 'field_currency': 'USD'}, Money(15.15, 'USD')),
        ),
    )
    def test_post_put_values(self, body, expected):
        serializer = self.get_serializer(NullMoneyFieldModel, data=body)
        serializer.is_valid()
        if IS_DRF_3:
            assert serializer.validated_data['field'] == expected
        else:
            assert Money(serializer.data['field'], serializer.data['field_currency']) == expected
