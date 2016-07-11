# coding: utf-8
from textwrap import dedent

from django import VERSION

import pytest


@pytest.mark.skipif(VERSION >= (1, 7), reason='Django 1.7+ has migration framework')
@pytest.mark.usefixtures('coveragerc')
class TestSouth:

    @pytest.fixture(autouse=True)
    def setup(self, testdir):
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

    def make_models(self, content):
        fd = self.project_root.join('models.py')
        fd.write(dedent(content))

    def test_create_initial(self, testdir):
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            field = MoneyField(max_digits=10, decimal_places=2)''')

        testdir.makepyfile(test_migration='''
        from django.core.management import call_command


        def test_create_initial():
            call_command('schemamigration', 'money_app', initial=True)

            migration = __import__('money_app.migrations.0001_initial', fromlist=['Migration'])

            models = migration.Migration.models['money_app.model']
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '10', 'decimal_places': '2', 'default_currency': u"'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})
        ''')
        result = testdir.runpytest_subprocess(
            '--ds', 'app_settings', '-s', '--verbose', '--cov', 'djmoney', '--cov-config', 'coveragerc.ini'
        )
        assert result.ret == 0

    def test_migrate_field(self, testdir):
        self.project_root.join('migrations/__init__.py').ensure()
        migration = self.project_root.join('migrations/0001_initial.py')
        migration.write(dedent('''
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.create_table(u'money_app_model', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_currency', self.gf('djmoney.models.fields.CurrencyField')()),
            ('field', self.gf('djmoney.models.fields.MoneyField')(default_currency='XYZ', decimal_places=2, max_digits=10)),
        ))
        db.send_create_signal(u'money_app', ['Model'])


    def backwards(self, orm):
        db.delete_table(u'money_app_model')


    models = {
        u'money_app.model': {
            'Meta': {'object_name': 'Model'},
            'field': ('djmoney.models.fields.MoneyField', [], {'default_currency': u"'XYZ'", 'decimal_places': '2', 'max_digits': '10'}),
            'field_currency': ('djmoney.models.fields.CurrencyField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['money_app']'''))
        self.make_models('''
        from django.db import models

        from djmoney.models.fields import MoneyField


        class Model(models.Model):
            field = MoneyField(max_digits=15, decimal_places=2)''')

        testdir.makepyfile(test_migration='''
        from django.core.management import call_command

        import pytest


        @pytest.mark.django_db
        def test_create_initial():
            call_command('schemamigration', 'money_app', auto=True)

            migration = __import__('money_app.migrations.0002_auto__chg_field_model_field', fromlist=['Migration'])

            models = migration.Migration.models['money_app.model']
            assert models['field'] == (
                'djmoney.models.fields.MoneyField',
                [],
                {'max_digits': '15', 'decimal_places': '2', 'default_currency': u"'XYZ'"}
            )
            assert models['field_currency'] == ('djmoney.models.fields.CurrencyField', [], {})

            call_command('migrate', 'money_app')
        ''')
        result = testdir.runpytest_subprocess(
            '--ds', 'app_settings', '-s', '--verbose', '--cov', 'djmoney', '--cov-config', 'coveragerc.ini'
        )
        assert result.ret == 0
