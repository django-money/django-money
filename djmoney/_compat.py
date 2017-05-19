# -*- coding: utf-8 -*-
# flake8: noqa
from django import VERSION
from django.db.models.manager import ManagerDescriptor


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
        # Python 3.2 & 3.3
        from imp import reload as reload_module


def setup_managers(sender):
    from .models.managers import money_manager

    if VERSION >= (1, 10):
        for manager in filter(lambda m: m.name == 'objects', sender._meta.managers):
            setattr(sender, manager.name, ManagerDescriptor(money_manager(manager)))
    else:
        sender.copy_managers([
            (_id, name, money_manager(manager))
            for _id, name, manager in sender._meta.concrete_managers if name == 'objects'
        ])
