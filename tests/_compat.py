# -*- coding: utf-8 -*-
# flake8: noqa

try:
    from mock import patch, Mock
except ImportError:
    from unittest.mock import patch, Mock
