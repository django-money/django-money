from django.conf import settings

from django.core import serializers as serializers

serializers.register_serializer("json", 'djmoney.serializers')
