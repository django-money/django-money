from djmoney import settings

from .base import SimpleExchangeBackend


class OpenExchangeRatesBackend(SimpleExchangeBackend):
    name = 'openexchangerates.org'
    url = settings.OPEN_EXCHANGE_RATES_URL

    def get_params(self):
        return {'app_id': settings.OPEN_EXCHANGE_RATES_APP_ID}
