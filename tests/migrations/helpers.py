"""
This module contains various helpers for migrations testing.
"""
import os


MIGRATION_NAME = "test"


def makemigrations():
    from django.core.management import call_command
    from django.db.migrations import questioner

    # We should answer yes for all migrations questioner questions
    questioner.input = lambda x: "y"

    os.system("find . -name \\*.pyc -delete")
    call_command("makemigrations", "money_app", name=MIGRATION_NAME)


def get_migration(name):
    return __import__("money_app.migrations.%s_%s" % (name, MIGRATION_NAME), fromlist=["Migration"]).Migration


def get_operations(migration_name):
    return get_migration(migration_name).operations


def migrate():
    from django.core.management import call_command

    call_command("migrate", "money_app")
