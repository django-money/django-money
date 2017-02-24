# coding: utf-8
"""
This module contains various helpers for migrations testing.
"""
from django import VERSION
from django.core.management import call_command


MIGRATION_NAME = 'test'


def makemigrations():
    if VERSION >= (1, 7):
        call_command('makemigrations', name=MIGRATION_NAME)
    else:
        try:
            call_command('schemamigration', 'money_app', MIGRATION_NAME, auto=True)
        except SystemExit:
            call_command('schemamigration', 'money_app', MIGRATION_NAME, initial=True)


def get_migration(name):
    return __import__('money_app.migrations.%s_%s' % (name, MIGRATION_NAME), fromlist=['Migration']).Migration


def get_operations(migration_name):
    return get_migration(migration_name).operations


def get_models(migration_name):
    return get_migration(migration_name).models['money_app.model']
