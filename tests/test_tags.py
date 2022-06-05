import django
from django.template import Context, Template, TemplateSyntaxError
from django.utils.translation import override

import pytest

from djmoney.money import Money
from djmoney.templatetags.djmoney import MoneyLocalizeNode


def render(template, context):
    return Template(template).render(Context(context))


class TestMoneyLocalizeNode:
    def test_repr(self):
        assert repr(MoneyLocalizeNode(Money(5, "EUR"))) == "<MoneyLocalizeNode 5 EUR>"

    def test_invalid_instance(self):
        with pytest.raises(Exception) as exc:
            MoneyLocalizeNode(Money(5, "EUR"), amount=15)
        assert str(exc.value) == 'You can define either "money" or the "amount" and "currency".'


@pytest.mark.parametrize(
    "template, context, error_text",
    (
        (
            '{% load djmoney %}{% money_localize "2.5" "PLN" as NEW_M and blabla %}{{NEW_M}}',
            {},
            "Wrong number of input data to the tag.",
        ),
        (
            "{% load djmoney %}{% money_localize money %}{{NEW_M}}",
            {"money": "Something else"},
            'The variable "money" must be an instance of Money.',
        ),
        (
            "{% load djmoney %}{% money_localize amount currency %}",
            {"amount": None, "currency": "PLN"},
            "You must define both variables: amount and currency.",
        ),
    ),
)
def test_invalid_input(template, context, error_text):
    with pytest.raises(TemplateSyntaxError) as exc:
        render(template, context)
    assert str(exc.value) == error_text


def assert_template(string, result, context=None):
    context = context or {}
    with override("pl"):
        assert render(string, context) == result


@pytest.mark.parametrize(
    "string, result, context",
    (
        ('{% load djmoney %}{% money_localize "2.5" "PLN" as NEW_M %}{{NEW_M}}', "2,50\xa0zł", {}),
        ('{% load djmoney %}{% money_localize "2.5" "PLN" %}', "2,50\xa0zł", {}),
        ("{% load djmoney %}{% money_localize amount currency %}", "2,60\xa0zł", {"amount": 2.6, "currency": "PLN"}),
        ("{% load djmoney %}{% money_localize money as NEW_M %}{{NEW_M}}", "2,30\xa0zł", {"money": Money(2.3, "PLN")}),
        (
            "{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}",
            "2,30\xa0zł",
            {"money": Money(2.3, "PLN")},
        ),
        (
            "{% load djmoney %}{% money_localize money off as NEW_M %}{{NEW_M}}",
            "0,00\xa0zł",
            {"money": Money(0, "PLN")},
        ),
        (
            # with a tag template "money_localize"
            "{% load djmoney %}{% money_localize money %}",
            "2,30\xa0zł",
            {"money": Money(2.3, "PLN")},
        ),
        (
            # without a tag template "money_localize"
            "{{ money }}",
            "2,30\xa0zł",
            {"money": Money(2.3, "PLN")},
        ),
        ("{% load djmoney %}{% money_localize money off %}", "2,30\xa0zł", {"money": Money(2.3, "PLN")}),
        ("{% load djmoney %}{% money_localize money on %}", "2,30\xa0zł", {"money": Money(2.3, "PLN")}),
        (
            # in django 2.0 we fail inside the for loop
            '{% load djmoney %}{% for i in "xxx" %}{% money_localize money %} {% endfor %}',
            "2,30\xa0zł 2,30\xa0zł 2,30\xa0zł ",
            {"money": Money(2.3, "PLN"), "test": "test"},
        ),
    ),
)
def test_tag(string, result, context):
    assert_template(string, result, context)


@pytest.mark.parametrize(
    "string, result, context",
    (
        (
            # money_localize has a default setting USE_L10N = True
            "{% load djmoney %}{% money_localize money %}",
            "2,30\xa0zł",
            {"money": Money(2.3, "PLN")},
        ),
        (
            # without a tag template "money_localize"
            "{{ money }}",
            "2,30\xa0zł",
            {"money": Money(2.3, "PLN")},
        ),
        ("{% load djmoney %}{% money_localize money on %}", "2,30\xa0zł", {"money": Money(2.3, "PLN")}),
    ),
)
def test_l10n_off(settings, string, result, context):
    # This test is only nice to run in older version of Django that do not either
    # complain that the setting is deprecated or as of Django 5.0 entirely ignores
    # this setting
    if django.VERSION < (4, 0):
        settings.USE_L10N = False
        assert_template(string, result, context)


def test_forced_l10n():
    mp = Money(2.3, "PLN")
    mp.use_l10n = True
    assert_template("{{ money }}", "2,30\xa0zł", {"money": mp})
