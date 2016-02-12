# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.helpers import AdminReadonlyField
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import ManyToManyRel
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ._compat import lookup_field, smart_unicode


def get_empty_value_display(cls):
    if hasattr(cls.model_admin, 'get_empty_value_display'):
        return cls.model_admin.get_empty_value_display()
    else:
        # Django < 1.9
        from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        return EMPTY_CHANGELIST_VALUE


def djmoney_contents(self):
    from django.contrib.admin.templatetags.admin_list import _boolean_icon

    field, obj, model_admin = self.field['field'], self.form.instance, self.model_admin

    try:
        f, attr, value = lookup_field(field, obj, model_admin)
    except (AttributeError, ValueError, ObjectDoesNotExist):
        result_repr = get_empty_value_display(self)
    else:
        if f is None:
            boolean = getattr(attr, 'boolean', False)
            if boolean:
                result_repr = _boolean_icon(value)
            else:
                result_repr = smart_unicode(value)
                if getattr(attr, 'allow_tags', False):
                    result_repr = mark_safe(result_repr)
        else:
            if value is None:
                result_repr = get_empty_value_display(self)
            elif isinstance(f.rel, ManyToManyRel):
                result_repr = ', '.join(map(str, value.all()))
            else:
                result_repr = smart_unicode(value)
    return conditional_escape(result_repr)


AdminReadonlyField.contents = djmoney_contents
