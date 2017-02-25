# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest


@pytest.mark.usefixtures('coveragerc')
class TestCurrencies:

    def assert_test_passed(self, testdir, lines):
        result = testdir.runpytest_subprocess(
            '--verbose', '-s',
            '--ds', 'app_settings',
            '--cov', 'djmoney',
            '--cov-config', 'coveragerc.ini',
        )
        result.stdout.fnmatch_lines(lines)

    def test_project_currencies(self, testdir):
        testdir.makepyfile(app_settings='''
        # -*- coding: utf-8 -*-
        INSTALLED_APPS = ['djmoney']
        CURRENCIES = ['USD', 'EUR']
        SECRET_KEY = 'foobar'
        ''')
        testdir.makepyfile('''
        def test():
            from djmoney.settings import CURRENCY_CHOICES

            assert CURRENCY_CHOICES == [('EUR', 'Euro'), ('USD', 'US Dollar')]
        ''')
        self.assert_test_passed(testdir, ['test_project_currencies.py::test PASSED'])

    def test_custom_currencies(self, testdir):
        testdir.makepyfile(app_settings='''
        # -*- coding: utf-8 -*-
        INSTALLED_APPS = ['djmoney']
        CURRENCIES = ['USD', 'EUR']
        CURRENCY_CHOICES = [('USD', 'USD $'), ('EUR', 'EUR €')]

        SECRET_KEY = 'foobar'
        ''')
        testdir.makepyfile('''
        # -*- coding: utf-8 -*-

        def test():
            from djmoney.settings import CURRENCY_CHOICES

            assert CURRENCY_CHOICES == [('EUR', 'EUR €'), ('USD', 'USD $')]
        ''')
        self.assert_test_passed(testdir, ['test_custom_currencies.py::test PASSED'])
