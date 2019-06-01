# -*- coding: utf-8 -*-
# flake8: noqa


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
    # Python 3.4+
    from importlib import reload as reload_module

try:
    from urllib2 import urlopen
    from urlparse import urlparse, parse_qsl, urlunparse
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import urlparse, parse_qsl, urlunparse


def setup_managers(sender):
    from .models.managers import money_manager

    default_manager_name = sender._meta.default_manager_name or "objects"
    for manager in filter(lambda m: m.name == default_manager_name, sender._meta.local_managers):
        money_manager(manager)
