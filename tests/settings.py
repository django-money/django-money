import warnings
from decimal import ROUND_HALF_EVEN

import moneyed
from moneyed.localization import _FORMATTER, DEFAULT


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
    "reversion",
    "tests.testapp",
]

SITE_ID = 1

SECRET_KEY = "foobar"

USE_L10N = True


_FORMATTER.add_sign_definition("pl_PL", moneyed.PLN, suffix=" zł")
_FORMATTER.add_sign_definition(DEFAULT, moneyed.PLN, suffix=" zł")
_FORMATTER.add_formatting_definition(
    "pl_PL",
    group_size=3,
    group_separator=" ",
    decimal_point=",",
    positive_sign="",
    trailing_positive_sign="",
    negative_sign="-",
    trailing_negative_sign="",
    rounding_method=ROUND_HALF_EVEN,
)

moneyed.add_currency("USDT", "000", "Tether", None)

OPEN_EXCHANGE_RATES_APP_ID = "test"
FIXER_ACCESS_KEY = "test"
