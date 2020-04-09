from importlib import reload as reload_module

from django.db import models

import djmoney.settings
from djmoney.models.fields import MoneyField


class TestCurrencies:
    def create_class(self, **field_kwargs):
        class SettingsModel(models.Model):
            field = MoneyField(**field_kwargs)

            class Meta:
                app_label = "test"

        return SettingsModel

    def assert_choices(self, expected):
        reload_module(djmoney.settings)
        assert djmoney.settings.CURRENCY_CHOICES == expected

    def test_project_currencies(self, settings):
        settings.CURRENCIES = ["USD", "EUR"]
        self.assert_choices([("EUR", "Euro"), ("USD", "US Dollar")])

    def test_custom_currencies(self, settings):
        settings.CURRENCIES = ["USD", "EUR"]
        settings.CURRENCY_CHOICES = [("USD", "USD $"), ("EUR", "EUR €")]
        self.assert_choices([("EUR", "EUR €"), ("USD", "USD $")])

    def test_default_currency(self, settings):
        settings.DEFAULT_CURRENCY = None
        klass = self.create_class(default_currency=None, max_digits=10, decimal_places=2, null=True)
        assert klass._meta.fields[2].default_currency is None
        instance = klass()
        assert instance.field is None
