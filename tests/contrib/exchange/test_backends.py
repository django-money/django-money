import pytest

from djmoney.contrib.exchange.models import ExchangeBackend

from .conftest import ExchangeTest


pytestmark = pytest.mark.django_db


class TestOpenExchangeRates(ExchangeTest):

    def test_get_rates(self):
        assert self.backend.get_rates() == self.expected

    def test_initial_update_rates(self):
        self.backend.update_rates()
        self.assert_rates()

    def test_second_update_rates(self):
        self.backend.update_rates()
        backend = ExchangeBackend.objects.get(name=self.backend.name)
        last_update = backend.last_update
        self.backend.update_rates()
        backend.refresh_from_db()
        assert last_update < backend.last_update
