# -*- coding: utf-8 -*-
from __future__ import absolute_import

import importlib
from decimal import Decimal

from django import template
from django.template import TemplateSyntaxError, VariableDoesNotExist

from djmoney import settings
from ..money import Money
from ..utils import MONEY_CLASSES


register = template.Library()


class MoneyLocalizeNode(template.Node):

    def __repr__(self):
        return '<MoneyLocalizeNode %d %s>' % (self.money.amount, self.money.currency)

    def __init__(self, money=None, amount=None, currency=None, use_l10n=None,
                 var_name=None, decimal_places=2):

        if money and (amount or currency):
            raise Exception('You can define either "money" or the "amount" and "currency".')

        self.money = money
        self.amount = amount
        self.currency = currency
        self.use_l10n = use_l10n
        self.var_name = var_name

        self.request = template.Variable('request')
        self.country_code = None
        self.decimal_places = decimal_places

    @classmethod
    def handle_token(cls, parser, token, no_decimal=False):

        tokens = token.contents.split()

        # default value
        var_name = None
        use_l10n = True

        # GET variable var_name
        if len(tokens) > 3:
            if tokens[-2] == 'as':
                var_name = parser.compile_filter(tokens[-1])
                # remove the already used data
                tokens = tokens[0:-2]

        # GET variable use_l10n
        if tokens[-1].lower() in ('on', 'off'):
            use_l10n = tokens[-1].lower() == 'on'
            # remove the already used data
            tokens.pop(-1)

        if len(tokens) < 2:
            raise TemplateSyntaxError('Wrong number of input data to the tag.')

        create_args = {
            'var_name': var_name,
            'use_l10n': use_l10n,
        }

        # GET variable money
        if len(tokens) == 2:
            create_args.update({
                'money': parser.compile_filter(tokens[1]),
            })

        # GET variable amount and currency
        elif len(tokens) == 3:
            create_args.update({
                'amount': parser.compile_filter(tokens[1]),
                'currency': parser.compile_filter(tokens[2]),
            })

        if no_decimal:
            create_args['decimal_places'] = 0

        return cls(**create_args)

    def render(self, context):

        money = self.money.resolve(context) if self.money else None
        amount = self.amount.resolve(context) if self.amount else None
        currency = self.currency.resolve(context) if self.currency else None

        try:
            request = self.request.resolve(context) if self.request else None
        except VariableDoesNotExist:
            request = None

        if request:
            try:
                self.country_code = getattr(request, 'country_code')
            except AttributeError:
                self.country_code = None

        if money is not None:
            if not isinstance(money, MONEY_CLASSES):
                raise TemplateSyntaxError('The variable "money" must be an instance of Money.')

        elif amount is not None and currency is not None:
            money = Money(Decimal(str(amount)), str(currency))
        else:
            raise TemplateSyntaxError('You must define both variables: amount and currency.')

        money.use_l10n = self.use_l10n
        money.decimal_places = self.decimal_places

        money = self._str_override_currency_sign(money)

        if self.var_name is None:
            return str(money)

        # as <var_name>
        context[self.var_name.token] = money
        return ''

    def _str_override_currency_sign(self, money):
        str_money = unicode(money)
        if hasattr(settings, 'CURRENCY_CONFIG_MODULE'):
            currency_config = importlib.import_module(settings.CURRENCY_CONFIG_MODULE)
            overrides = currency_config.override_currency_by_location

            if self.country_code and self.country_code.upper() in overrides.keys():
                currencies = overrides.get(self.country_code)
                if currencies and str(money.currency) in currencies.keys():
                    values = currencies[str(money.currency)]
                    str_money = str(money).replace(values[0], values[1])

        return str_money


@register.tag
def money_localize(parser, token):
    """
    Usage::

        {% money_localize <money_object> [ on(default) | off ] [as var_name] %}
        {% money_localize <amount> <currency> [ on(default) | off ] [as var_name] %}

    Example:

        The same effect:
        {% money_localize money_object %}
        {% money_localize money_object on %}

        Assignment to a variable:
        {% money_localize money_object on as NEW_MONEY_OBJECT %}

        Formatting the number with currency:
        {% money_localize '4.5' 'USD' %}

    Return::

        Money object

    """
    return MoneyLocalizeNode.handle_token(parser, token)


@register.tag
def money_localize_no_decimal(parser, token):
    """
    Usage::

        {% money_localize_no_decimal <money_object> [as var_name] %}
    Example:

        {% money_localize_no_decimal money_object %}
        {% money_localize_no_decimal money_object as NEW_MONEY_OBJECT %}

    Return::

        MoneyPatched object

    """
    return MoneyLocalizeNode.handle_token(parser, token, no_decimal=True)
