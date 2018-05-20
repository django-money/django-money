from decimal import Decimal
from textwrap import dedent

from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import Rate, convert_money, get_rate
from djmoney.money import Money


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('source, target, expected', (
    ('USD', 'USD', 1),
    ('USD', 'EUR', 2),
    ('EUR', 'USD', Decimal('0.5')),
))
def test_get_rate(backend, source, target, expected):
    Rate.objects.create(currency='EUR', value=2, backend=backend)
    assert get_rate(source, target) == expected


def test_unknown_currency():
    with pytest.raises(MissingRate, match='Rate USD \\-\\> EUR does not exist'):
        get_rate('USD', 'EUR')


def test_string_representation(backend):
    assert str(backend) == backend.name


def test_bad_configuration(settings):
    settings.INSTALLED_APPS.remove('djmoney.contrib.exchange')
    with pytest.raises(ImproperlyConfigured):
        convert_money(Money(1, 'USD'), 'EUR')


def test_without_installed_exchange(testdir):
    """
    If there is no 'djmoney.contrib.exchange' in INSTALLED_APPS importing `Money` should not cause a RuntimeError.
    Details: GH-385.
    """
    testdir.mkpydir('money_app')
    testdir.makepyfile(app_settings='''
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
        }
    }
    INSTALLED_APPS = ['djmoney']
    SECRET_KEY = 'foobar'
    ''')
    result = testdir.runpython_c(dedent('''
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'app_settings'
    from django import setup

    setup()
    from djmoney.money import Money
    print(Money(1, 'USD'))
    '''))
    result.stdout.fnmatch_lines(['US$1.00'])
