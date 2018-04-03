import json
from decimal import Decimal

from djmoney import settings

from .base import BaseExchangeBackend


class OpenExchangeRatesBackend(BaseExchangeBackend):
    name = 'openexchangerates.org'

    def __init__(self, base_url=settings.OPEN_EXCHANGE_RATES_URL, app_id=settings.OPEN_EXCHANGE_RATES_APP_ID,
                 base_currency=settings.BASE_CURRENCY):
        self.base_url = base_url
        self.app_id = app_id
        self.base_currency = base_currency

    def get_rates(self):
        response = self.get_response(base=self.base_currency, app_id=self.app_id)
        data = json.loads(response, parse_float=Decimal)
        return data['rates']
