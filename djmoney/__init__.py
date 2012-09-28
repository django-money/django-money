from django.db import models
from django.utils.encoding import smart_unicode
from django.utils import formats
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.util import lookup_field
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.db.models.fields.related import ManyToManyRel

from django.contrib.admin import util as admin_util


def djmoney_display_for_field(value, field):
    from django.contrib.admin.templatetags.admin_list import _boolean_icon
    from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE

    try:
        if field.flatchoices:
            return dict(field.flatchoices).get(value, EMPTY_CHANGELIST_VALUE)
        # NullBooleanField needs special-case null-handling, so it comes
        # before the general null test.
        elif isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
            return _boolean_icon(value)
        elif value is None:
            return EMPTY_CHANGELIST_VALUE
        elif isinstance(field, models.DateTimeField):
            return formats.localize(timezone.localtime(value))
        elif isinstance(field, models.DateField) or isinstance(field, models.TimeField):
            return formats.localize(value)
        elif isinstance(field, models.DecimalField):
            return formats.number_format(value, field.decimal_places)
        elif isinstance(field, models.FloatField):
            return formats.number_format(value)
        else:
            return smart_unicode(value)
    except:
            return smart_unicode(value)
admin_util.display_for_field = djmoney_display_for_field

def djmoney_contents(self):
    from django.contrib.admin.templatetags.admin_list import _boolean_icon
    from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
    field, obj, model_admin = self.field['field'], self.form.instance, self.model_admin

    try:
        f, attr, value = lookup_field(field, obj, model_admin)
    except (AttributeError, ValueError, ObjectDoesNotExist):
        result_repr = EMPTY_CHANGELIST_VALUE
    else:
        if f is None:
            boolean = getattr(attr, "boolean", False)
            if boolean:
                result_repr = _boolean_icon(value)
            else:
                result_repr = smart_unicode(value)
                if getattr(attr, "allow_tags", False):
                    result_repr = mark_safe(result_repr)
        else:
            if value is None:
                result_repr = EMPTY_CHANGELIST_VALUE
            elif isinstance(f.rel, ManyToManyRel):
                result_repr = ", ".join(map(unicode, value.all()))
            else:
                result_repr = djmoney_display_for_field(value, f)
    return conditional_escape(result_repr)

from django.contrib.admin.helpers import AdminReadonlyField
AdminReadonlyField.contents = djmoney_contents
