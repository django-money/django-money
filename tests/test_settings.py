# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import djmoney.settings
from djmoney._compat import reload_module


class TestCurrencies:

    def assert_choices(self, expected):
        reload_module(djmoney.settings)
        assert djmoney.settings.CURRENCY_CHOICES == expected

    def test_project_currencies(self, settings):
        settings.CURRENCIES = ['USD', 'EUR']
        self.assert_choices([('EUR', 'Euro'), ('USD', 'US Dollar')])

    def test_custom_currencies(self, settings):
        settings.CURRENCIES = ['USD', 'EUR']
        settings.CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €')]
        self.assert_choices([('EUR', 'EUR €'), ('USD', 'USD $')])
