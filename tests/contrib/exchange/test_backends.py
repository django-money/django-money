import pytest

from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend
from djmoney.contrib.exchange.models import ExchangeBackend

from .conftest import EXPECTED_RATES, ExchangeTest


pytestmark = pytest.mark.django_db


class TestOpenExchangeRates(ExchangeTest):

    @pytest.fixture()
    def openexchangerate(self):
        return OpenExchangeRatesBackend()

    def test_get_rates(self, openexchangerate):
        assert openexchangerate.get_rates() == EXPECTED_RATES

    def test_initial_update_rates(self, openexchangerate):
        openexchangerate.update_rates()
        self.assert_rates()

    def test_second_update_rates(self, openexchangerate):
        openexchangerate.update_rates()
        backend = ExchangeBackend.objects.get(name=openexchangerate.name)
        last_update = backend.last_update
        openexchangerate.update_rates()
        backend.refresh_from_db()
        assert last_update < backend.last_update
