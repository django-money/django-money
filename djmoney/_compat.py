# -*- coding: utf-8 -*-
# flake8: noqa
import functools

from django import VERSION
from django.db.models.manager import ManagerDescriptor


try:
    import django.contrib.admin.utils as admin_utils
except ImportError:
    # Django < 1.5
    import django.contrib.admin.util as admin_utils

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:
    # Django < 1.5
    LOOKUP_SEP = '__'

try:
    from django.db.models.expressions import BaseExpression
except ImportError:
    # Django < 1.8
    from django.db.models.expressions import ExpressionNode as BaseExpression

try:
    from django.contrib.admin.utils import lookup_field
except ImportError:
    from django.contrib.admin.util import lookup_field

try:
    from django.utils.encoding import smart_unicode
except ImportError:
    # Python 3
    from django.utils.encoding import smart_text as smart_unicode

try:
    from django.db.models import Case, Func, Value, When
except ImportError:
    Case, Func, Value, When = None, None, None, None

try:
    from django.utils.six import wraps
except ImportError:
    # Django 1.5, and some versions from 1.4.x branch
    def wraps(wrapped, assigned=functools.WRAPPER_ASSIGNMENTS, updated=functools.WRAPPER_UPDATES):

        def wrapper(f):
            f = functools.wraps(wrapped)(f)
            f.__wrapped__ = wrapped
            return f

        return wrapper

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

if VERSION >= (1, 7):
    from django.utils.deconstruct import deconstructible
else:
    def deconstructible(cls):
        return cls


def split_expression(expr):
    """
    Returns lhs and rhs of the expression.
    """
    if VERSION < (1, 8):
        return expr.children
    else:
        return expr.lhs, expr.rhs


def set_expression_rhs(expr, value):
    """
    Sets right hand side value of the expression.
    """
    if VERSION < (1, 8):
        expr.children[1] = value
    else:
        expr.rhs.value = value


def get_field_names(model):
    """
    Returns a set of field names associated with the model.
    """
    opts = model._meta
    if VERSION < (1, 8):
        return opts.get_all_field_names()
    else:
        return set(field.name for field in opts.get_fields())


def get_fields(model):
    """
    Returns a set of field instances associated with the model.
    """
    opts = model._meta
    if VERSION < (1, 8):
        return opts.fields
    else:
        return opts.get_fields()


def resolve_field(qs, parts, opts, alias):
    if VERSION < (1, 6):
        return qs.setup_joins(parts, opts, alias, False)[0]
    elif VERSION[:2] == (1, 6):
        return qs.names_to_path(parts, opts, True, True)[1]
    else:
        return qs.names_to_path(parts, opts, True, fail_on_missing=False)[1]


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
