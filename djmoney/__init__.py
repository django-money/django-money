# -*- coding: utf-8 -*-

__version__ = '0.9dev0'


try:
    from .contrib.django_rest_framework import register_money_field

    register_money_field()
except ImportError:
    pass
