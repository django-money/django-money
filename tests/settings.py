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

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

ROOT_URLCONF = "tests.urls"

# This now defaults to True and raises RemovedInDjango50Warning
if django.VERSION < (4, 0):
    USE_L10N = True


moneyed.add_currency(code="USDT", numeric="000", name="Tether")

OPEN_EXCHANGE_RATES_APP_ID = "test"
FIXER_ACCESS_KEY = "test"

DEFAULT_CURRENCY = "USD"

# Additional setting for callables with different defaults
TEST_DEFAULT_CURRENCY = "EUR"
