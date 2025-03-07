import django.contrib.admin.helpers as admin_helpers
import django.contrib.admin.templatetags.admin_list as admin_list
import django.contrib.admin.utils as admin_utils

from .models.fields import MoneyField


MODULES_TO_PATCH = [admin_utils, admin_helpers, admin_list]


def setup_admin_integration():
    original_display_for_field = admin_utils.display_for_field

    def display_for_field(value, field, empty, avoid_link=False):
        if isinstance(field, MoneyField):
            return str(value)
        return original_display_for_field(value, field, empty, avoid_link=False)

    for mod in MODULES_TO_PATCH:
        setattr(mod, "display_for_field", display_for_field)
