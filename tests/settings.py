# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
from decimal import ROUND_HALF_EVEN

from django import VERSION

import moneyed
from moneyed.localization import _FORMATTER, DEFAULT


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
]

warnings.simplefilter('ignore', Warning)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'djmoney',
    'reversion',

    'tests.testapp'
]
# Application will not start on Django 2.0
if VERSION < (2, 0):
    INSTALLED_APPS.append('djmoney_rates')


SITE_ID = 1
ROOT_URLCONF = 'core.urls'

SECRET_KEY = 'foobar'

USE_L10N = True


_FORMATTER.add_sign_definition('pl_PL', moneyed.PLN, suffix=' zł')
_FORMATTER.add_sign_definition(DEFAULT, moneyed.PLN, suffix=' zł')
_FORMATTER.add_formatting_definition(
    'pl_PL', group_size=3, group_separator=' ', decimal_point=',',
    positive_sign='', trailing_positive_sign='',
    negative_sign='-', trailing_negative_sign='',
    rounding_method=ROUND_HALF_EVEN
)
