# -*- coding: utf-8 -*-
from rest_framework import VERSION


VERSION = [int(i) for i in VERSION.split('.')]

IS_DRF_3 = VERSION >= [3, 0, 0]
