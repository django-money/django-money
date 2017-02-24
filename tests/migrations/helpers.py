# coding: utf-8
"""
This module contains various helpers for migrations testing.
"""
from django import VERSION
from django.core.management import call_command


def makemigrations():
    if VERSION >= (1, 7):
        call_command('makemigrations')
    else:
        try:
            call_command('schemamigration', 'money_app', 'auto', auto=True)
        except SystemExit:
            call_command('schemamigration', 'money_app', initial=True)


def get_migration(name):
    migrations = __import__('money_app.migrations').migrations
    for member in dir(migrations):
        if member[:4] == name:
            return getattr(migrations, member).Migration
    return __import__('money_app.migrations.%s' % name, fromlist=['Migration']).Migration


def get_operations(migration_name):
    return get_migration(migration_name).operations


def get_models(migration_name):
    return get_migration(migration_name).models['money_app.model']
