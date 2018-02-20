# -*- coding: utf-8 -*-
# flake8: noqa
from django import VERSION


try:
    from django.utils.encoding import smart_unicode
except ImportError:
    # Python 3
    from django.utils.encoding import smart_text as smart_unicode

try:
    string_types = (basestring,)
    text_type = unicode
except NameError:
    string_types = (str, bytes)
    text_type = str

try:
    # Python 2
    reload_module = reload
except NameError:
    try:
        # Python 3.4+
        from importlib import reload as reload_module
    except ImportError:
        # Python 3.3
        from imp import reload as reload_module


try:
    from django.core.validators import DecimalValidator

    class MoneyValidator(DecimalValidator):

        def __call__(self, value):
            return super(MoneyValidator, self).__call__(value.amount)

except ImportError:
    MoneyValidator = None


def setup_managers(sender):
    from .models.managers import money_manager

    if VERSION >= (1, 11):
        for manager in filter(lambda m: m.name == 'objects', sender._meta.local_managers):
            money_manager(manager)
    else:
        sender.copy_managers([
            (_id, name, money_manager(manager))
            for _id, name, manager in sender._meta.concrete_managers if name == 'objects'
        ])
