# -*- coding: utf-8 -*-
from django.forms import MultiWidget, Select, TextInput

from ..settings import CURRENCY_CHOICES


__all__ = ('MoneyWidget',)


class MoneyWidget(MultiWidget):

    def __init__(self, choices=CURRENCY_CHOICES, amount_widget=TextInput, currency_widget=None, default_currency=None,
                 *args, **kwargs):
        self.default_currency = default_currency
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super(MoneyWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is not None:
            return [value.amount, value.currency]
        return [None, self.default_currency]

    # Needed for Django 1.5.x, where Field doesn't have the '_has_changed' method.
    # But it mustn't run on Django 1.6, where it doesn't work and isn't needed.

    if hasattr(TextInput, '_has_changed'):  # noqa
        # This is a reimplementation of the MoneyField.has_changed,
        # but for the widget.
        def _has_changed(self, initial, data):
            if initial is None:
                initial = ['' for x in range(0, len(data))]
            else:
                if not isinstance(initial, list):
                    initial = self.decompress(initial)

            amount_widget, currency_widget = self.widgets
            amount_initial, currency_initial = initial

            try:
                amount_data = data[0]
            except IndexError:
                amount_data = None

            if amount_widget._has_changed(amount_initial, amount_data):
                return True

            try:
                currency_data = data[1]
            except IndexError:
                currency_data = None

            if currency_widget._has_changed(currency_initial, currency_data) and amount_data:
                return True

            return False
