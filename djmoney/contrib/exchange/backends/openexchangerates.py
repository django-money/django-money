from djmoney import settings

from .base import SimpleExchangeBackend


class OpenExchangeRatesBackend(SimpleExchangeBackend):
    name = 'openexchangerates.org'

    def __init__(self, base_url=settings.OPEN_EXCHANGE_RATES_URL, app_id=settings.OPEN_EXCHANGE_RATES_APP_ID):
        self.base_url = base_url
        self.app_id = app_id

    def get_params(self):
        return {'app_id': self.app_id}
