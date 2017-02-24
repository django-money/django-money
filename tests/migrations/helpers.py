# coding: utf-8
"""
This module contains various helpers for migrations testing.
"""
import os
from os.path import abspath, join

from django import VERSION
from django.core.management import call_command


if VERSION >= (1, 7):
    from django import setup
    setup()


MIGRATION_NAME = 'test'


def makemigrations():
    os.system('find . -name \*.pyc -delete')
    if VERSION >= (1, 10):
        call_command('makemigrations', 'money_app', name=MIGRATION_NAME)
    elif VERSION >= (1, 7):
        run_migration_command()
    else:
        if '0001_test.py' not in os.listdir(join(abspath(os.curdir), 'money_app/migrations')):
            kwargs = {'initial': True}
        else:
            kwargs = {'auto': True}
        call_command('schemamigration', 'money_app', MIGRATION_NAME, **kwargs)


def run_migration_command():
    """
    In Django 1.8 & 1.9 first argument name clashes with command option.
    In Django 1.7 there is no built-in option to name a migration.
    """
    from django.core.management.commands.makemigrations import Command

    if VERSION < (1, 8):

        class Command(Command):

            def write_migration_files(self, changes):
                migration = list(changes.items())[0][1][0]
                migration.name = migration.name.split('_')[0] + '_' + MIGRATION_NAME
                super(Command, self).write_migration_files(changes)

    Command().execute('money_app', name=MIGRATION_NAME, verbosity=1)


def get_migration(name):
    return __import__('money_app.migrations.%s_%s' % (name, MIGRATION_NAME), fromlist=['Migration']).Migration


def get_operations(migration_name):
    return get_migration(migration_name).operations


def get_models(migration_name):
    return get_migration(migration_name).models['money_app.model']


def migrate():
    if VERSION < (1, 7):
        call_command('syncdb')
    call_command('migrate', 'money_app')
