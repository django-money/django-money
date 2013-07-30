import json
from StringIO import StringIO
from decimal import Decimal
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.core.serializers.python import Serializer
from django.core.serializers.python import _get_model
from django.core.serializers.base import DeserializationError
from djmoney.models.fields import MoneyField

### This works with reversion but may break with loaddata and dumpdata
### Needs more work!
### /benjaoming 2013-07-30

Serializer = Serializer

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
        for obj in json.load(stream):
            money_fields = {}
            Model = _get_model(obj["model"])
            for (field_name, field_value) in obj["fields"].iteritems():
                field = Model._meta.get_field(field_name)
                if isinstance(field, MoneyField):
                    money_fields[field_name] = Decimal(
                        field_value.split(" ")[0])

            obj["fields"] = dict(
                filter(lambda (k, v): k not in money_fields.keys(),
                       obj["fields"].items()))

            for obj in PythonDeserializer([obj], **options):
                for field, value in money_fields.items():
                    setattr(obj.object, field, value)
                yield obj

    except GeneratorExit:
        raise
    except Exception, e:
        # Map to deserializer error
        raise DeserializationError(e)
