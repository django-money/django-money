from django.core.management import call_command

import pytest

from djmoney.contrib.exchange.models import Rate

from .conftest import ExchangeTest, FixedOneBackend, FixedTwoBackend


pytestmark = pytest.mark.django_db

BACKEND_PATH = FixedOneBackend.__module__ + "." + FixedOneBackend.__name__


class TestCommand(ExchangeTest):
    def test_update_rates(self):
        call_command("update_rates")
        self.assert_rates()


def test_custom_backend():
    call_command("update_rates", backend=BACKEND_PATH)
    assert Rate.objects.filter(currency="EUR", value=1).exists()


@pytest.mark.usefixtures("two_backends_data")
class TestClearRates:
    def test_for_specific_backend(self):
        call_command("clear_rates", backend=BACKEND_PATH)
        assert not Rate.objects.filter(backend=FixedOneBackend.name).exists()
        assert Rate.objects.filter(backend=FixedTwoBackend.name).exists()

    def test_for_all(self):
        call_command("clear_rates", all=True)
        assert not Rate.objects.exists()
