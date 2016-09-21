# -*- coding: utf-8 -*-
import pytest


@pytest.mark.usefixtures('coveragerc')
def test_project_currencies(testdir):
    testdir.makepyfile(test_settings='''
    INSTALLED_APPS = ['djmoney']
    CURRENCIES = ['USD', 'EUR']
    SECRET_KEY = 'foobar'
    ''')
    testdir.makepyfile('''
    def test_project_currencies():
        from djmoney.settings import CURRENCY_CHOICES

        assert CURRENCY_CHOICES == [('EUR', 'Euro'), ('USD', 'US Dollar')]
    ''')
    result = testdir.runpytest_subprocess(
        '--verbose', '-s',
        '--ds', 'test_settings',
        '--cov', 'djmoney',
        '--cov-config', 'coveragerc.ini',
    )
    assert 'test_project_currencies.py::test_project_currencies PASSED' in result.stdout.lines
