import warnings

import django

import moneyed


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.contrib.auth.context_processors.auth"]},
    }
]

warnings.simplefilter("ignore", Warning)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "djmoney",
    "djmoney.contrib.exchange",
    "tests.testapp",
]

SITE_ID = 1

SECRET_KEY = "foobar"


# This now defaults to True and raises RemovedInDjango50Warning
if django.VERSION < (4, 0):
    USE_L10N = True


moneyed.add_currency(code="USDT", numeric="000", name="Tether")

OPEN_EXCHANGE_RATES_APP_ID = "test"
FIXER_ACCESS_KEY = "test"
