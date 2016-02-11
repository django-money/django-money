# -*- coding: utf-8 -*-
# flake8: noqa
from django import VERSION


if VERSION >= (1, 7):
    from reversion import revisions as reversion
else:
    import reversion
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch
