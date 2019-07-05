# -*- coding: utf-8 -*-
import json
import sys

from django.core.serializers.base import DeserializationError
from django.core.serializers.json import Serializer as JSONSerializer
from django.utils import six

from djmoney.money import Money

from .models.fields import MoneyField, LinkedCurrencyMoneyField
from .utils import get_currency_field_name


Serializer = JSONSerializer


def Deserializer(stream_or_string, **options):  # noqa
    """
    Deserialize a stream or string of JSON data.
    """
    # Local imports to allow using modified versions of `_get_model`
    # It could be patched in runtime via `unittest.mock.patch` for example
    from django.core.serializers.python import Deserializer as PythonDeserializer, _get_model

    ignore = options.pop("ignorenonexistent", False)

    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode("utf-8")
    try:
        for obj in json.loads(stream_or_string):
            try:
                Model = _get_model(obj["model"])
            except DeserializationError:
                if ignore:
                    continue
                else:
                    raise
            money_fields = {}
            fields = {}
            field_names = {field.name for field in Model._meta.get_fields()}
            for (field_name, field_value) in six.iteritems(obj["fields"]):
                if ignore and field_name not in field_names:
                    # skip fields no longer on model
                    continue
                field = Model._meta.get_field(field_name)
                if isinstance(field, LinkedCurrencyMoneyField) and field_value is not None:
                    currency_field_name = get_currency_field_name(field_name, field=field)
                    money_fields[field_name] = Money(field_value, get_currency_from_obj(Model, obj, currency_field_name))
                elif isinstance(field, MoneyField) and field_value is not None:
                    money_fields[field_name] = Money(field_value, obj["fields"][get_currency_field_name(field_name)])
                else:
                    fields[field_name] = field_value
            obj["fields"] = fields

            for inner_obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    setattr(inner_obj.object, field, value)
                yield inner_obj
    except (GeneratorExit, DeserializationError):
        raise
    except Exception as exc:
        six.reraise(DeserializationError, DeserializationError(exc), sys.exc_info()[2])


def get_currency_from_obj(Model, obj, currency_field_name):
    if "__" in currency_field_name:
        data = obj["fields"]
        RelatedModel = None
        *related_attrs, currency_attr = currency_field_name.split("__")
        for related_attr in related_attrs:
            if RelatedModel:
                data = RelatedModel.objects.values_list(f"{related_attr}_id", flat=True).get(pk=foreign_key_id)
                foreign_key_id = data
            else:
                foreign_key_id = data[related_attr]
            RelatedModel = getattr(RelatedModel or Model, related_attr).field.target_field.model
        # TODO: this may cause DoesNotExist errors if the fixture hasn't loaded related models yet.
        currency = RelatedModel.objects.values_list(currency_attr, flat=True).get(pk=foreign_key_id)
    else:
        currency = obj.__dict__[currency_field_name]
    return currency