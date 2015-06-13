#-*- encoding: utf-8 -*-
from setuptools import setup

from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(name="django-money",
      version="0.7.0",
      description="Adds support for using money and currency fields in django models and forms. Uses py-moneyed as the money implementation.",
      url="https://github.com/jakewins/django-money",
      maintainer='Greg Reinbach',
      maintainer_email='greg@reinbach.com',
      packages=["djmoney",
                "djmoney.forms",
                "djmoney.models",
                "djmoney.templatetags",
                "djmoney.tests"],
      install_requires=['setuptools',
                        'Django >= 1.4, < 1.9',
                        'py-moneyed > 0.4',
                        'six'],
      platforms=['Any'],
      keywords=['django', 'py-money', 'money'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Framework :: Django", ],
      tests_require=['tox>=1.6.0'],
      cmdclass={'test': Tox},
      )
