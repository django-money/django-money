# coding: utf-8

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
