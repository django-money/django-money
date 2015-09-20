from __future__ import unicode_literals
from warnings import warn

from django.core import validators
from django.forms import MultiValueField, DecimalField, ChoiceField
from moneyed.classes import Money

from .widgets import MoneyWidget
from ..settings import CURRENCY_CHOICES


__all__ = ('MoneyField',)


class MoneyField(MultiValueField):

    # Django 1.5 compat:
    if not hasattr(MultiValueField, 'empty_values'):
        empty_values = list(validators.EMPTY_VALUES)

    def __init__(self, currency_widget=None, currency_choices=CURRENCY_CHOICES,
                 choices=CURRENCY_CHOICES, max_value=None, min_value=None,
                 max_digits=None, decimal_places=None, *args, **kwargs):

        # choices does not make sense in this context, it would mean we had
        # to replace two widgets with one widget dynamically... which is a
        # mess. Instead, we let currency_choices be the same as choices and
        # raise a warning.
        if currency_choices != CURRENCY_CHOICES:
            warn('currency_choices will be deprecated in favor of choices', PendingDeprecationWarning)
            choices = currency_choices

        amount_field = DecimalField(max_value, min_value, max_digits, decimal_places, *args, **kwargs)
        currency_field = ChoiceField(choices=choices)

        # TODO: No idea what currency_widget is supposed to do since it doesn't
        # even receive currency choices as input. Somehow it's supposed to be
        # instantiated from outside. Hard to tell.
        if currency_widget:
            self.widget = currency_widget
        else:
            self.widget = MoneyWidget(
                amount_widget=amount_field.widget,
                currency_widget=currency_field.widget
            )

        # The two fields that this widget comprises
        fields = (amount_field, currency_field)
        super(MoneyField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            if not self.required and data_list[0] in self.empty_values:
                return None
            else:
                return Money(*data_list[:2])
        return None

    def _has_changed(self, initial, data):
        # TODO: What on earth is going on here!?

        # ChoiceField._has_changed returns True always here, so we rely solely
        # on the DecimalField. Based on MultiValueField.
        if initial is None:
            initial = [''] * len(data)
            # initial = ['' for x in range(0, len(data))]
        else:
            if not isinstance(initial, list):
                initial = self.widget.decompress(initial)
        return self.fields[0]._has_changed(initial[0], data[0])
