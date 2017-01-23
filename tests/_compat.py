# -*- coding: utf-8 -*-
# flake8: noqa
import reversion


if reversion.VERSION >= (2, 0):
    from reversion.revisions import create_revision, register
    from reversion.models import Version

    get_deleted = Version.objects.get_deleted
elif reversion.VERSION >= (1, 10):
    from reversion.revisions import get_deleted, create_revision, register
else:
    from reversion import get_deleted, create_revision, register
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch
