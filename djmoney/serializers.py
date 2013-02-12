from django.core import serializers

from django.core.serializers.json import Serializer
from django.core.serializers.python import Deserializer as PythonDeserializer,\
    _get_model
from StringIO import StringIO
from django.core.serializers.base import DeserializationError
from django.utils import simplejson

from models.fields import MoneyField
from moneyed import Money
from decimal import Decimal
from django.db.models.fields import DecimalField

def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    try:
        obj_list = []
        for obj in simplejson.load(stream):
            money_fields = {}
            Model = _get_model(obj["model"])
            for (field_name, field_value) in obj["fields"].iteritems():
                field = Model._meta.get_field(field_name)
                if isinstance(field, MoneyField):
                    money_fields[field_name] = Decimal(field_value.split(" ")[0])
                
            obj["fields"] = dict(filter(lambda (k,v): k not in money_fields.keys(), obj["fields"].items()))

            for obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    print obj.object
                    setattr(obj.object, field, value)
                yield obj
    
    except GeneratorExit:
        raise

