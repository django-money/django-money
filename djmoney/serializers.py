# coding=utf-8
import json

from django.core.serializers.python import Deserializer as PythonDeserializer
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import _get_model
from django.utils import six

from djmoney.models.fields import MoneyField
from djmoney.utils import get_currency_field_name
from moneyed import Money

Serializer = JSONSerializer


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        for obj in json.loads(stream_or_string):
            money_fields = {}
            fields = {}
            Model = _get_model(obj["model"])
            for (field_name, field_value) in six.iteritems(obj['fields']):
                field = Model._meta.get_field(field_name)
                if isinstance(field, MoneyField) and field_value is not None:
                    money_fields[field_name] = Money(field_value, obj['fields'][get_currency_field_name(field_name)])
                else:
                    fields[field_name] = field_value
            obj['fields'] = fields

            for obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    setattr(obj.object, field, value)
                yield obj
    except GeneratorExit:
        raise
