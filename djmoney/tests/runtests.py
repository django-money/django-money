'''
Created on May 7, 2011

@author: jake
'''
import sys
import os
import unittest
import django.conf


def setup():
    test_folder = os.path.abspath(os.path.dirname(__file__))
    src_folder = os.path.abspath(test_folder + "/../")
    sys.path.insert(0, test_folder)
    sys.path.insert(0, src_folder)

    os.environ[django.conf.ENVIRONMENT_VARIABLE] = "settings"

    from django.test.utils import setup_test_environment
    setup_test_environment()

    from django.db import connection
    connection.creation.create_test_db()


def tear_down():
    from django.db import connection
    connection.creation.destroy_test_db("not_needed")

    from django.test.utils import teardown_test_environment
    teardown_test_environment()

if __name__ == "__main__":

    setup()

    import tests
    unittest.main(module=tests)

    tear_down()
