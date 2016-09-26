# -*- coding: utf-8 -*-
from textwrap import dedent

from django import VERSION

import pytest


INITIAL_SOUTH_MIGRATION = '''# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.create_table('money_app_model', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_currency', self.gf('djmoney.models.fields.CurrencyField')()),
            ('field', self.gf('djmoney.models.fields.MoneyField')(default_currency='XYZ', decimal_places=2, max_digits=10)),
        ))
        db.send_create_signal('money_app', ['Model'])


    def backwards(self, orm):
        db.delete_table('money_app_model')


    models = {
        'money_app.model': {
            'Meta': {'object_name': 'Model'},
            'field': ('djmoney.models.fields.MoneyField', [], {'default_currency': "'XYZ'", 'decimal_places': '2', 'max_digits': '10'}),
            'field_currency': ('djmoney.models.fields.CurrencyField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['money_app']'''


@pytest.mark.skipif(VERSION >= (1, 7), reason='Django 1.7+ has migration framework')
@pytest.mark.usefixtures('coveragerc')
class TestSouth:
    """
    Tests for South-based migrations on Django < 1.7.
    """

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
        INSTALLED_APPS = ['djmoney', 'south', 'money_app']
        SECRET_KEY = 'foobar'
        ''')
        testdir.makepyfile(helpers='''
        from django.core.management import call_command


        def schemamigration(initial=False):
            if initial:
                call_command('schemamigration', 'money_app', initial=True)
            else:
                call_command('schemamigration', 'money_app', 'auto', auto=True)


        def migrate():
            call_command('migrate', 'money_app')


        def syncdb():
            call_command('syncdb')

        def get_migration(name):
            return __import__('money_app.migrations.%s' % name, fromlist=['Migration'])


        def get_models(migration_name):
            migration = get_migration(migration_name)
            return migration.Migration.models['money_app.model']
        ''')

    def make_models(self, content):
        """
        Creates models.py file.
        """
        fd = self.project_root.join('models.py')
        fd.write(dedent(content))

    def make_migration(self, name, content):
        self.project_root.join('migrations/__init__.py').ensure()
        migration = self.project_root.join('migrations/%s.py' % name)
        migration.write(dedent(content))

    def migrate(self):
        self.run('from helpers import syncdb, migrate; syncdb(); migrate()', False)

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

    def test_create_initial(self):
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            field = MoneyField(max_digits=10, decimal_places=2)''')

        self.run('''
        from helpers import get_models, schemamigration


        def test_create_initial():
            schemamigration(initial=True)
            models = get_models('0001_initial')
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '10', 'decimal_places': '2', 'default_currency': "'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        ''')
        self.migrate()

    def test_alter_field(self):
        self.make_migration('0001_initial', INITIAL_SOUTH_MIGRATION)
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            field = MoneyField(max_digits=15, decimal_places=2)''')

        self.run('''
        import pytest

        from helpers import get_models, schemamigration


        @pytest.mark.django_db
        def test_alter_field():
            schemamigration()
            models = get_models('0002_auto')
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '15', 'decimal_places': '2', 'default_currency': "'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        ''')
        self.migrate()

    def test_add_field(self):
        self.make_migration('0001_initial', INITIAL_SOUTH_MIGRATION)
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            field = MoneyField(max_digits=10, decimal_places=2)
            value = MoneyField(max_digits=5, decimal_places=2, default_currency='GBP')''')
        self.run('''
        import pytest

        from helpers import get_models, schemamigration


        @pytest.mark.django_db
        def test_add_field():
            schemamigration()
            models = get_models('0002_auto')
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
        self.migrate()

    def test_remove_field(self):
        self.make_migration('0001_initial', INITIAL_SOUTH_MIGRATION)
        self.make_models('''
        from django.db import models


        class Model(models.Model):
            pass''')
        self.run('''
        import pytest

        from helpers import get_models, schemamigration


        @pytest.mark.django_db
        def test_remove_field():
            schemamigration()
            models = get_models('0002_auto')
            assert models == {
                'Meta': {'object_name': 'Model'},
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
            }
        ''')
        self.migrate()
