from decimal import Decimal
from textwrap import dedent

from django.core.exceptions import ImproperlyConfigured

import pytest

from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import _get_rate, convert_money, get_rate
from djmoney.money import Currency, Money
from tests._compat import patch


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('source, target, expected', (
    ('USD', 'USD', 1),
    ('USD', 'EUR', 2),
    ('EUR', 'USD', Decimal('0.5')),
    (Currency('USD'), 'USD', 1),
    ('USD', Currency('USD'), 1),
))
@pytest.mark.usefixtures('simple_rates')
def test_get_rate(source, target, expected):
    assert get_rate(source, target) == expected


def test_unknown_currency():
    with pytest.raises(MissingRate, match='Rate USD \\-\\> EUR does not exist'):
        get_rate('USD', 'EUR')


def test_string_representation(backend):
    assert str(backend) == backend.name


@pytest.mark.usefixtures('simple_rates')
def test_cache():
    with patch('djmoney.contrib.exchange.models._get_rate', wraps=_get_rate) as original:
        assert get_rate('USD', 'USD') == 1
        assert original.call_count == 1
        assert get_rate('USD', 'USD') == 1
        assert original.call_count == 1


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
