# -*- coding: utf-8 -*-
from django.core import serializers


serializers.register_serializer('json', 'djmoney.serializers')
