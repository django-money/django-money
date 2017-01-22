# -*- coding: utf-8 -*-
# flake8: noqa
from django import VERSION


if VERSION >= (1, 9):
    from reversion import revisions as reversion
    from reversion.models import Version

    get_deleted = Version.objects.get_deleted
else:
    import reversion

    get_deleted = reversion.get_deleted
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch
