#!/usr/bin/env python
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
    SOUTH_TESTS_MIGRATE=True,
)

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)

# If you use South for migrations, uncomment this to monkeypatch
# syncdb to get migrations to run.
from south.management.commands import patch_for_test_db_setup
patch_for_test_db_setup()

failures = test_runner.run_tests(['djmoney', ])
if failures:
    sys.exit(failures)
