from djmoney import settings

from .base import SimpleExchangeBackend


class FixerBackend(SimpleExchangeBackend):
    name = 'fixer.io'
    url = settings.FIXER_URL

    def get_params(self):
        return {'access_key': settings.FIXER_ACCESS_KEY}
