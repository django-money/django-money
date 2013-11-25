#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.conf import settings

settings.configure(
    DEBUG=True,
#    AUTH_USER_MODEL='testdata.CustomUser',
    DATABASES={
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
         }
    },
    SITE_ID=1,
    ROOT_URLCONF=None,
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'djmoney',
        'djmoney.tests.testapp',
        'south',
        'reversion',
    ),
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


from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)

# If you use South for migrations, uncomment this to monkeypatch
# syncdb to get migrations to run.
from south.management.commands import patch_for_test_db_setup
patch_for_test_db_setup()

failures = test_runner.run_tests(['djmoney', ])
if failures:
    sys.exit(failures)


## Run py.tests
# Compatibility testing patches on the py-moneyed
import pytest
pytest.main()
