from djmoney import settings

from .base import BaseExchangeBackend


class FixerBackend(BaseExchangeBackend):
    name = 'fixer.io'

    def __init__(self, base_url=settings.FIXER_URL, access_key=settings.FIXER_ACCESS_KEY,
                 base_currency=settings.BASE_CURRENCY):
        self.base_url = base_url
        self.access_key = access_key
        self.base_currency = base_currency

    def get_rates(self):
        response = self.get_response(base=self.base_currency, access_key=self.access_key)
        return self.parse_json(response)['rates']
