# -*- coding: utf-8 -*-
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import djmoney


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass into py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


test_requirements = [
    'mock',
    'pytest>=3.1.0',
    'pytest-django',
    'pytest-pythonpath',
    'pytest-cov',
]

extras_requirements = {
    'test': test_requirements,
}


if sys.version_info[0] == 2:
    test_requirements.append('mock')

setup(
    name='django-money',
    version=djmoney.__version__,
    description='Adds support for using money and currency fields in django models and forms. '
                'Uses py-moneyed as the money implementation.',
    url='https://github.com/django-money/django-money',
    maintainer='Greg Reinbach',
    maintainer_email='greg@reinbach.com',
    packages=[
        'djmoney',
        'djmoney.forms',
        'djmoney.models',
        'djmoney.templatetags',
        'djmoney.contrib',
        'djmoney.contrib.django_rest_framework',
        'djmoney.contrib.exchange',
        'djmoney.contrib.exchange.backends',
        'djmoney.contrib.exchange.management',
        'djmoney.contrib.exchange.migrations',
    ],
    install_requires=[
        'setuptools',
        'Django>=1.8',
        'py-moneyed>=0.7'
    ],
    platforms=['Any'],
    keywords=['django', 'py-money', 'money'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
    ],
    tests_require=test_requirements,
    extras_require=extras_requirements,
    cmdclass={'test': PyTest},
)
