import pytest

from djmoney.contrib.exchange.tasks import update_rates

from .conftest import ExchangeTest


pytestmark = pytest.mark.django_db


class TestTask(ExchangeTest):

    def test_task(self):
        update_rates()
        self.assert_rates()
