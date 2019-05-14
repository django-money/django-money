# coding: utf-8
import django.contrib.admin.helpers as admin_helpers
import django.contrib.admin.templatetags.admin_list as admin_list
import django.contrib.admin.utils as admin_utils
from django import VERSION

from ._compat import text_type
from .models.fields import MoneyField


MODULES_TO_PATCH = [admin_utils, admin_helpers, admin_list]


def setup_admin_integration():
    original_display_for_field = admin_utils.display_for_field

    if VERSION[:2] == (1, 8):

        def display_for_field(value, field):
            if isinstance(field, MoneyField):
                return text_type(value)
            return original_display_for_field(value, field)

    else:

        def display_for_field(value, field, empty):
            if isinstance(field, MoneyField):
                return text_type(value)
            return original_display_for_field(value, field, empty)

    for mod in MODULES_TO_PATCH:
        setattr(mod, "display_for_field", display_for_field)
