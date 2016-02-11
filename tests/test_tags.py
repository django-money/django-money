# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import override

import pytest
from moneyed import Money

from djmoney.models.fields import MoneyPatched


def assert_template(string, result, context=None):
    context = context or {}
    with override('pl'):
        assert Template(string).render(Context(context)) == result


@pytest.mark.parametrize(
    'string, result, context',
    (
        (
            '{% load djmoney %}{% money_localize "2.5" "PLN" as NEW_M %}{{NEW_M}}',
            '2,50 zł',
            {}
        ),
        (
            '{% load djmoney %}{% money_localize "2.5" "PLN" %}',
            '2,50 zł',
            {}
        ),
        (
            '{% load djmoney %}{% money_localize amount currency %}',
            '2,60 zł',
            {'amount': 2.6, 'currency': 'PLN'}
        ),
        (
            '{% load djmoney %}{% money_localize money as NEW_M %}{{NEW_M}}',
            '2,30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            '{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}',
            '2.30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            '{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}',
            '0.00 zł',
            {'money': Money(0, 'PLN')}
        ),
        (
            # with a tag template "money_localize"
            '{% load djmoney %}{% money_localize money %}',
            '2,30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            # without a tag template "money_localize"
            '{{ money }}',
            '2,30 zł',
            {'money': MoneyPatched(2.3, 'PLN')}
        ),
        (
            '{% load djmoney %}{% money_localize money off %}',
            '2.30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            '{% load djmoney %}{% money_localize money on %}',
            '2,30 zł',
            {'money': Money(2.3, 'PLN')}
        )
    )
)
def test_tag(string, result, context):
    assert_template(string, result, context)


@pytest.mark.parametrize(
    'string, result, context',
    (
        (
            # money_localize has a default setting USE_L10N = True
            '{% load djmoney %}{% money_localize money %}',
            '2,30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            # without a tag template "money_localize"
            '{{ money }}',
            '2.30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
        (
            '{% load djmoney %}{% money_localize money on %}',
            '2,30 zł',
            {'money': Money(2.3, 'PLN')}
        ),
    )
)
def test_l10n_off(settings, string, result, context):
    settings.USE_L10N = False
    assert_template(string, result, context)


def test_forced_l10n():
    mp = MoneyPatched(2.3, 'PLN')
    mp.use_l10n = True
    assert_template('{{ money }}', '2,30 zł', {'money': mp})
