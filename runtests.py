#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.conf import settings

# Detect if django.db.migrations is supported
from django import VERSION as DJANGO_VERSION
NATIVE_MIGRATIONS = (DJANGO_VERSION >= (1, 7))


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'djmoney',
    'djmoney.tests.testapp',
    'reversion',
)

if not NATIVE_MIGRATIONS:
    INSTALLED_APPS += (
        'south',
    )

settings.configure(
    DEBUG=True,
    DATABASES={
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
         }
    },
    SITE_ID=1,
    ROOT_URLCONF=None,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
    ),
    INSTALLED_APPS=INSTALLED_APPS,
    USE_TZ=True,
    USE_L10N=True,
    SOUTH_TESTS_MIGRATE=True,
)

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


try:
    from django.test.simple import DjangoTestSuiteRunner
except ImportError:
    from django.test.runner import DiscoverRunner as DjangoTestSuiteRunner

test_runner = DjangoTestSuiteRunner(verbosity=1, failfast=False)

# Native migrations are present in Django 1.7+
# This also requires initializing the app registry with django.setup()
# If native migrations are not present, initialize South and configure it for running the test suite
if NATIVE_MIGRATIONS:
    from django import setup
    setup()
else:
    from south.management.commands import patch_for_test_db_setup
    patch_for_test_db_setup()

if len(sys.argv) > 1:
    tests = sys.argv[1:]
else:
    tests = ['djmoney']
failures = test_runner.run_tests(tests)
if failures:
    sys.exit(failures)


## Run py.tests
# Compatibility testing patches on the py-moneyed
import pytest
failures = pytest.main()

if failures:
    sys.exit(failures)
