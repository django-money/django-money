# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import warnings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

warnings.simplefilter('ignore', Warning)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djmoney',
    'testapp'
)

SITE_ID = 1
ROOT_URLCONF = 'core.urls'

SECRET_KEY = 'foobar'

USE_L10N = True

import moneyed
from moneyed.localization import _FORMATTER, DEFAULT
from decimal import ROUND_HALF_EVEN

_FORMATTER.add_sign_definition('pl_PL', moneyed.PLN, suffix=' zł')
_FORMATTER.add_sign_definition(DEFAULT, moneyed.PLN, suffix=' zł')
_FORMATTER.add_formatting_definition(
    "pl_PL", group_size=3, group_separator=" ", decimal_point=",",
    positive_sign="", trailing_positive_sign="",
    negative_sign="-", trailing_negative_sign="",
    rounding_method=ROUND_HALF_EVEN)
