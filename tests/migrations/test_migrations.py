# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join
from textwrap import dedent

from django import VERSION

import pytest


HELPERS = join(dirname(abspath(__file__)), 'helpers.py')


@pytest.mark.usefixtures('coveragerc')
class BaseMigrationTests:
    installed_apps = ['djmoney', 'money_app']

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
        with open(HELPERS) as fd:
            testdir.makepyfile(helpers=fd.read())
        self.project_root.join('migrations/__init__.py').ensure()
        testdir.makeconftest('''
        import pytest

        @pytest.fixture(autouse=True)
        def enable_db_access(db):
            pass''')

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
        self.make_migration_file()

    def run(self, content, check=True):
        """
        Executes given test code in subprocess.
        """
        self.testdir.makepyfile(test_migration=content)
        result = self.testdir.runpytest_subprocess(
            '--ds', 'app_settings', '-s', '--verbose',
            '--cov-append', '--cov', 'djmoney', '--cov-config', 'coveragerc.ini'
        )
        if check:
            assert result.ret == 0

    def make_migration_file(self):
        self.run('from helpers import makemigrations; makemigrations();', False)
        
    def make_default_migration(self):
        self.make_migration(field='MoneyField(max_digits=10, decimal_places=2)')


@pytest.mark.skipif(VERSION >= (1, 7), reason='Django 1.7+ has migration framework')
class TestSouth(BaseMigrationTests):
    """
    Tests for South-based migrations on Django < 1.7.
    """
    installed_apps = BaseMigrationTests.installed_apps + ['south']

    def test_create_initial(self):
        self.make_default_migration()
        self.run('''
        from helpers import get_models


        def test_create_initial():
            models = get_models('0001')
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '10', 'decimal_places': '2', 'default_currency': "'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        ''')

    def test_alter_field(self):
        self.make_default_migration()
        self.make_migration(field='MoneyField(max_digits=15, decimal_places=2)')
        self.run('''
        from helpers import get_models


        def test_alter_field():
            models = get_models('0002')
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '15', 'decimal_places': '2', 'default_currency': "'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        ''')

    def test_add_field(self):
        self.make_default_migration()
        self.make_migration(
            field='MoneyField(max_digits=10, decimal_places=2)',
            value="MoneyField(max_digits=5, decimal_places=2, default_currency='GBP')"
        )
        self.run('''
        from helpers import get_models


        def test_add_field():
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
        ''')

    def test_remove_field(self):
        self.make_default_migration()
        self.make_migration()
        self.run('''
        from helpers import get_models


        def test_remove_field():
            models = get_models('0002')
            assert models == {
                'Meta': {},
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
            }
        ''')


@pytest.mark.skipif(VERSION < (1, 7), reason='Django 1.7+ has migration framework')
class TestMigrationFramework(BaseMigrationTests):

    def test_create_initial(self):
        self.make_default_migration()
        self.run('''
        from django.db import migrations
        from django.db.models.fields import AutoField

        from djmoney.models.fields import MoneyField, CurrencyField
        from helpers import get_operations


        def test_create_initial():
            operations = get_operations('0001')
            assert len(operations) == 1

            assert isinstance(operations[0], migrations.CreateModel)

            fields = sorted(operations[0].fields)
            assert len(fields) == 3
            assert fields[0][0] == 'field'
            assert isinstance(fields[0][1], MoneyField)
            assert fields[1][0] == 'field_currency'
            assert isinstance(fields[1][1], CurrencyField)
        ''')

    def test_add_field(self):
        self.make_migration()
        self.make_default_migration()
        self.run('''
        from django.db import migrations

        from djmoney.models.fields import MoneyField, CurrencyField
        from helpers import get_operations


        def test_add_field():
            operations = get_operations('0002')
            assert len(operations) == 2

            assert isinstance(operations[0], migrations.AddField)
            assert isinstance(operations[0].field, MoneyField)
            assert isinstance(operations[1], migrations.AddField)
            assert isinstance(operations[1].field, CurrencyField)
        ''')

    def test_alter_field(self):
        self.make_default_migration()
        self.make_migration(field='MoneyField(max_digits=15, decimal_places=2)')
        self.run('''
        from django.db import migrations

        from djmoney.models.fields import MoneyField
        from helpers import get_operations


        def test_alter_field():
            operations = get_operations('0002')
            assert len(operations) == 1
            assert isinstance(operations[0], migrations.AlterField)
            assert isinstance(operations[0].field, MoneyField)
            assert operations[0].field.max_digits == 15
        ''')

    def test_remove_field(self):
        self.make_default_migration()
        self.make_migration()
        self.run('''
        from django.db import migrations

        from djmoney.models.fields import MoneyField, CurrencyField
        from helpers import get_operations


        def test_remove_field():
            operations = get_operations('0002')
            assert len(operations) == 2
            assert isinstance(operations[0], migrations.RemoveField)
            assert operations[0].name == 'field'
            assert isinstance(operations[1], migrations.RemoveField)
            assert operations[1].name == 'field_currency'
        ''')
