# coding: utf-8
from djmoney.models.fields import MoneyField


def setup_admin_integration():
    import django.contrib.admin.utils

    original_display_for_field = django.contrib.admin.utils.display_for_field

    def display_for_field(value, field, empty):
        if isinstance(field, MoneyField):
            return str(value)
        return original_display_for_field(value, field, empty)

    django.contrib.admin.utils.display_for_field = display_for_field
