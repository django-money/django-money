# -*- coding: utf-8 -*-
# flake8: noqa
from django import VERSION
from django.db.models.manager import ManagerDescriptor


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
    from django.db.models.expressions import Expression
except ImportError:
    # Django < 1.8
    from django.db.models.sql.expressions import SQLEvaluator as Expression

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
    string_types = (basestring,)
except NameError:
    string_types = (str, bytes)


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


def get_fields(model):
    """
    Returns a set of fields associated to the model.
    """
    opts = model._meta
    if VERSION < (1, 8):
        return opts.get_all_field_names()
    else:
        return set(field.name for field in opts.get_fields())


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
