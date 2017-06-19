# -*- coding: utf-8 -*-
import json

from django.core.serializers.base import DeserializationError
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import (
    Deserializer as PythonDeserializer,
    _get_model,
)
from django.utils import six

from moneyed import Money

from ._compat import get_field_names
from .models.fields import MoneyField
from .utils import get_currency_field_name


Serializer = JSONSerializer


def Deserializer(stream_or_string, **options):  # noqa
    """
    Deserialize a stream or string of JSON data.
    """
    ignore = options.pop('ignorenonexistent', False)

    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        for obj in json.loads(stream_or_string):
            try:
                Model = _get_model(obj['model'])
            except DeserializationError:
                if ignore:
                    continue
                else:
                    raise
            money_fields = {}
            fields = {}
            field_names = get_field_names(Model)
            for (field_name, field_value) in six.iteritems(obj['fields']):
                if ignore and field_name not in field_names:
                    # skip fields no longer on model
                    continue
                field = Model._meta.get_field(field_name)
                if isinstance(field, MoneyField) and field_value is not None:
                    money_fields[field_name] = Money(field_value, obj['fields'][get_currency_field_name(field_name)])
                else:
                    fields[field_name] = field_value
            obj['fields'] = fields

            for inner_obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    setattr(inner_obj.object, field, value)
                yield inner_obj
    except GeneratorExit:
        raise
