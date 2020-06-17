import os
from textwrap import dedent

from django.db import migrations

import pytest

import tests
from djmoney.models.fields import CurrencyField, MoneyField

from .helpers import get_operations


class TestMigrationFramework:
    installed_apps = ["djmoney", "money_app"]
    migration_output = ["*Applying money_app.0001_test... OK*", "*Applying money_app.0002_test... OK*"]

    @pytest.fixture(autouse=True)
    def setup(self, testdir):
        """
        Creates application module, helpers and settings file with basic config.
        """
        self.testdir = testdir
        self.project_root = testdir.mkpydir("money_app")
        testdir.makepyfile(
            app_settings="""
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': 'test.db',
                }
            }
            INSTALLED_APPS = %s
            SECRET_KEY = 'foobar'
            """
            % str(self.installed_apps)
        )
        self.project_root.join("migrations/__init__.py").ensure()
        testdir.syspathinsert()

    def make_models(self, content):
        """
        Creates models.py file.
        """
        fd = self.project_root.join("models.py")
        fd.write(dedent(content))

    def make_migration(self, **fields):
        """
        Creates a model with provided fields and creates a migration for it.
        """
        if fields:
            fields_definition = ";".join("=".join([field, definition]) for field, definition in fields.items())
        else:
            fields_definition = "pass"
        self.make_models(
            """
            from django.db import models

            from djmoney.models.fields import MoneyField


            class Model(models.Model):
                %s"""
            % fields_definition
        )
        tests_path = os.path.dirname(os.path.dirname(tests.__file__))
        return self.run(
            "import sys; sys.path.append('{}');".format(tests_path)
            + "from tests.migrations.helpers import makemigrations; makemigrations();"
        )

    def make_default_migration(self, field="MoneyField(max_digits=10, decimal_places=2, null=True)"):
        return self.make_migration(field=field)

    def run(self, content):
        return self.testdir.runpython_c(
            dedent(
                """
        import os
        os.environ['DJANGO_SETTINGS_MODULE'] = 'app_settings'
        from django import setup

        setup()
        %s
        """
                % content
            )
        )

    def create_instance(self):
        self.run(
            """
        from money_app.models import Model
        from djmoney.money import Money

        Model.objects.create(field=Money(10, 'USD'))"""
        )

    def migrate(self):
        tests_path = os.path.dirname(os.path.dirname(tests.__file__))
        return self.run(
            "import sys; sys.path.append('{}');".format(tests_path)
            + "from tests.migrations.helpers import migrate; migrate();"
        )

    def assert_migrate(self, output=None):
        """
        Runs migrations and checks if 2 migrations were applied.
        """
        if output is None:
            output = self.migration_output
        migration = self.migrate()
        migration.stdout.fnmatch_lines(output)

    def test_create_initial(self):
        migration = self.make_default_migration()
        migration.stdout.fnmatch_lines(["*Migrations for 'money_app':*", "*0001_test.py*", "*- Create model Model*"])
        operations = get_operations("0001")
        assert len(operations) == 1

        assert isinstance(operations[0], migrations.CreateModel)

        fields = sorted(operations[0].fields)
        assert len(fields) == 3
        assert fields[0][0] == "field"
        assert isinstance(fields[0][1], MoneyField)
        assert fields[1][0] == "field_currency"
        assert isinstance(fields[1][1], CurrencyField)
        migration = self.migrate()
        migration.stdout.fnmatch_lines(["*Applying money_app.0001_test... OK*"])

    def test_add_field(self):
        self.make_migration()
        migration = self.make_default_migration()
        migration.stdout.fnmatch_lines(
            [
                "*Migrations for 'money_app':*",
                "*0002_test.py*",
                "*- Add field field to model*",
                "*- Add field field_currency to model*",
            ]
        )

        operations = get_operations("0002")
        assert len(operations) == 2
        assert isinstance(operations[0], migrations.AddField)
        assert isinstance(operations[0].field, MoneyField)
        assert isinstance(operations[1], migrations.AddField)
        assert isinstance(operations[1].field, CurrencyField)
        self.assert_migrate()

    def test_alter_field(self):
        self.make_default_migration()
        migration = self.make_migration(field="MoneyField(max_digits=15, decimal_places=2, null=True)")
        migration.stdout.fnmatch_lines(
            ["*Migrations for 'money_app':*", "*0002_test.py*", "*- Alter field field on model*"]
        )

        operations = get_operations("0002")
        assert len(operations) == 1
        assert isinstance(operations[0], migrations.AlterField)
        assert isinstance(operations[0].field, MoneyField)
        assert operations[0].field.max_digits == 15
        self.assert_migrate()

    def test_remove_field(self):
        self.make_default_migration()
        migration = self.make_migration()
        migration.stdout.fnmatch_lines(
            [
                "*Migrations for 'money_app':*",
                "*0002_test.py*",
                "*- Remove field field from model*",
                "*- Remove field field_currency from model*",
            ]
        )

        operations = get_operations("0002")
        assert len(operations) == 2
        assert isinstance(operations[0], migrations.RemoveField)
        assert operations[0].name == "field"
        assert isinstance(operations[1], migrations.RemoveField)
        assert operations[1].name == "field_currency"
        self.assert_migrate()

    def test_rename_field(self):
        self.make_default_migration()
        self.assert_migrate(["*Applying money_app.0001_test... OK*"])
        self.create_instance()
        migration = self.make_migration(new_field="MoneyField(max_digits=10, decimal_places=2, null=True)")
        migration.stdout.fnmatch_lines(
            [
                "*Migrations for 'money_app':*",
                "*0002_test.py*",
                "*- Rename field field on model to new_field*",
                "*- Rename field field_currency on model to new_field_currency*",
            ]
        )
        self.assert_migrate(["*Applying money_app.0002_test... OK*"])
        result = self.run(
            """
        from money_app.models import Model

        instance = Model.objects.get()
        print(instance.new_field)
        """
        )
        result.stdout.fnmatch_lines(["US$10.00"])

    def test_migrate_to_moneyfield(self):
        self.make_default_migration(field="models.DecimalField(max_digits=10, decimal_places=2, null=True)")
        migration = self.make_migration(field="MoneyField(max_digits=10, decimal_places=2, null=True)")
        migration.stdout.fnmatch_lines(
            ["*Migrations for 'money_app':*", "*0002_test.py*", "*- Add field field_currency to model*"]
        )
        self.assert_migrate()

    def test_migrate_from_moneyfield(self):
        self.make_default_migration()
        migration = self.make_migration(field="models.DecimalField(max_digits=10, decimal_places=2, null=True)")
        migration.stdout.fnmatch_lines(
            ["*Migrations for 'money_app':*", "*0002_test.py*", "*- Remove field field_currency from model*"]
        )
        self.assert_migrate()
