import codecs
import os
import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

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


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


def find_version():
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", read("djmoney/__init__.py"), re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find __version__ string.")


setup(
    name="django-money",
    version=find_version(),
    packages=find_packages(include=["djmoney", "djmoney.*"]),
    platforms=["Any"],
    cmdclass={"test": PyTest},
)
