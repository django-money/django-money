# coding: utf-8
import django.contrib.admin.utils as admin_utils

from ._compat import text_type
from .models.fields import MoneyField


def setup_admin_integration():
    original_display_for_field = admin_utils.display_for_field

    def display_for_field(value, field, empty):
        if isinstance(field, MoneyField):
            return text_type(value)
        return original_display_for_field(value, field, empty)

    admin_utils.display_for_field = display_for_field
