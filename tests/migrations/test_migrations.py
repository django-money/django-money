# -*- coding: utf-8 -*-
from textwrap import dedent

from django import VERSION

import pytest

from djmoney.models.fields import CurrencyField, MoneyField

from .helpers import get_models, get_operations


if VERSION >= (1, 7):
    from django.db import migrations
else:
    migrations = None


@pytest.mark.usefixtures('coveragerc')
class BaseMigrationTests:
    installed_apps = ['djmoney', 'money_app']
    migration_output = ()

    @pytest.fixture(autouse=True)
    def setup(self, testdir):
        """
        Creates application module, helpers and settings file with basic config.
        """
        self.testdir = testdir
        self.project_root = testdir.mkpydir('money_app')
        testdir.makepyfile(app_settings='''
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
        INSTALLED_APPS = %s
        SECRET_KEY = 'foobar'
        ''' % str(self.installed_apps))
        self.project_root.join('migrations/__init__.py').ensure()
        testdir.syspathinsert()

    def make_models(self, content):
        """
        Creates models.py file.
        """
        fd = self.project_root.join('models.py')
        fd.write(dedent(content))

    def make_migration(self, **fields):
        """
        Creates a model with provided fields and creates a migration for it.
        """
        if fields:
            fields_definition = ';'.join(
                '='.join([field, definition]) for field, definition in fields.items()
            )
        else:
            fields_definition = 'pass'
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            %s''' % fields_definition)
        return self.run('from tests.migrations.helpers import makemigrations; makemigrations();')

    def make_default_migration(self):
        return self.make_migration(field='MoneyField(max_digits=10, decimal_places=2)')

    def run(self, content):
        # To collect coverage data from the call
        self.testdir.makepyfile(test_migration=content)
        return self.testdir.runpytest_subprocess(
            '--ds', 'app_settings', '-s', '--verbose',
            '--cov-append', '--cov', 'djmoney', '--cov-config', 'coveragerc.ini'
        )

    def migrate(self):
        return self.run('from tests.migrations.helpers import migrate; migrate();')

    def assert_migrate(self):
        """
        Runs migrations and checks if 2 migrations were applied.
        """
        migration = self.migrate()
        migration.stdout.fnmatch_lines(self.migration_output)


@pytest.mark.skipif(VERSION >= (1, 7), reason='Django 1.7+ has migration framework')
class TestSouth(BaseMigrationTests):
    """
    Tests for South-based migrations on Django < 1.7.
    """
    installed_apps = BaseMigrationTests.installed_apps + ['south']
    migration_output = [
        '* - Migrating forwards to 0002_test.*',
        '*> money_app:0001_test*',
        '*> money_app:0002_test*',
        '*- Loading initial data for money_app.*',
    ]

    def test_create_initial(self):
        migration = self.make_default_migration()
        migration.stderr.fnmatch_lines([
            '*Added model money_app.Model*',
            '*Created 0001_test.py*'
        ])

        models = get_models('0001')
        assert models['field'] == (
            'djmoney.models.fields.MoneyField',
            [],
            {
                'max_digits': '10',
                'decimal_places': '2',
                'default_currency': "'XYZ'"
            }
        )
        assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        migration = self.migrate()
        migration.stdout.fnmatch_lines([
            '*Creating table south_migrationhistory*',
            '* - Migrating forwards to 0001_test.*',
            '*> money_app:0001_test*',
        ])

    def test_alter_field(self):
        self.make_default_migration()
        migration = self.make_migration(field='MoneyField(max_digits=15, decimal_places=2)')
        migration.stderr.fnmatch_lines([
            '*~ Changed field field on money_app.Model*',
            '*Created 0002_test.py*',
        ])

        models = get_models('0002')
        assert models['field'] == (
            'djmoney.models.fields.MoneyField',
            [],
            {'max_digits': '15', 'decimal_places': '2', 'default_currency': "'XYZ'"}
        )
        assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        self.assert_migrate()

    def test_add_field(self):
        self.make_default_migration()
        migration = self.make_migration(
            field='MoneyField(max_digits=10, decimal_places=2)',
            value="MoneyField(max_digits=5, decimal_places=2, default_currency='GBP')"
        )
        migration.stderr.fnmatch_lines(['*+ Added field value_currency on money_app.Model*'])
        migration.stderr.fnmatch_lines([
            '*+ Added field value on money_app.Model*',
            '*Created 0002_test.py*',
        ])

        models = get_models('0002')
        assert models['field'] == (
            'djmoney.models.fields.MoneyField',
            [],
            {'max_digits': '10', 'decimal_places': '2', 'default_currency': "'XYZ'"}
        )
        assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        assert models['value'] == (
            'djmoney.models.fields.MoneyField',
            [],
            {'max_digits': '5', 'decimal_places': '2', 'default_currency': "'GBP'"}
        )
        assert models['value_currency'] == ('djmoney.models.fields.CurrencyField', [], {'default': "'GBP'"})
        self.assert_migrate()

    def test_remove_field(self):
        self.make_default_migration()
        migration = self.make_migration()
        migration.stderr.fnmatch_lines(['*- Deleted field field_currency on money_app.Model*'])
        migration.stderr.fnmatch_lines([
            '*- Deleted field field on money_app.Model*',
            '*Created 0002_test.py*',
        ])

        models = get_models('0002')
        assert models == {
            'Meta': {'object_name': 'Model'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
        self.assert_migrate()


@pytest.mark.skipif(VERSION < (1, 7), reason='Django 1.7+ has migration framework')
class TestMigrationFramework(BaseMigrationTests):
    migration_output = [
        '*Applying money_app.0001_test... OK*',
        '*Applying money_app.0002_test... OK*',
    ]

    def test_create_initial(self):
        migration = self.make_default_migration()
        migration.stdout.fnmatch_lines([
            "*Migrations for 'money_app':*",
            '*0001_test.py*',
            '*- Create model Model*',
        ])
        operations = get_operations('0001')
        assert len(operations) == 1

        assert isinstance(operations[0], migrations.CreateModel)

        fields = sorted(operations[0].fields)
        assert len(fields) == 3
        assert fields[0][0] == 'field'
        assert isinstance(fields[0][1], MoneyField)
        assert fields[1][0] == 'field_currency'
        assert isinstance(fields[1][1], CurrencyField)
        migration = self.migrate()
        migration.stdout.fnmatch_lines(['*Applying money_app.0001_test... OK*'])

    def test_add_field(self):
        self.make_migration()
        migration = self.make_default_migration()
        migration.stdout.fnmatch_lines([
            "*Migrations for 'money_app':*",
            '*0002_test.py*',
            '*- Add field field to model*',
            '*- Add field field_currency to model*',
        ])

        operations = get_operations('0002')
        assert len(operations) == 2
        assert isinstance(operations[0], migrations.AddField)
        assert isinstance(operations[0].field, MoneyField)
        assert isinstance(operations[1], migrations.AddField)
        assert isinstance(operations[1].field, CurrencyField)
        self.assert_migrate()

    def test_alter_field(self):
        self.make_default_migration()
        migration = self.make_migration(field='MoneyField(max_digits=15, decimal_places=2)')
        migration.stdout.fnmatch_lines([
            "*Migrations for 'money_app':*",
            '*0002_test.py*',
            '*- Alter field field on model*',
        ])

        operations = get_operations('0002')
        assert len(operations) == 1
        assert isinstance(operations[0], migrations.AlterField)
        assert isinstance(operations[0].field, MoneyField)
        assert operations[0].field.max_digits == 15
        self.assert_migrate()

    def test_remove_field(self):
        self.make_default_migration()
        migration = self.make_migration()
        migration.stdout.fnmatch_lines([
            "*Migrations for 'money_app':*",
            '*0002_test.py*',
            '*- Remove field field from model*',
            '*- Remove field field_currency from model*',
        ])

        operations = get_operations('0002')
        assert len(operations) == 2
        assert isinstance(operations[0], migrations.RemoveField)
        assert operations[0].name == 'field'
        assert isinstance(operations[1], migrations.RemoveField)
        assert operations[1].name == 'field_currency'
        self.assert_migrate()
