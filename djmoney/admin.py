# coding: utf-8
from django import VERSION

from ._compat import admin_utils, text_type
from .models.fields import MoneyField


def setup_admin_integration():
    original_display_for_field = admin_utils.display_for_field

    if VERSION < (1, 9):

        def display_for_field(value, field):
            if isinstance(field, MoneyField):
                return text_type(value)
            return original_display_for_field(value, field)

    else:

        def display_for_field(value, field, empty):
            if isinstance(field, MoneyField):
                return text_type(value)
            return original_display_for_field(value, field, empty)

    admin_utils.display_for_field = display_for_field
