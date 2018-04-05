from djmoney import settings

from .base import SimpleExchangeBackend


class FixerBackend(SimpleExchangeBackend):
    name = 'fixer.io'

    def __init__(self, base_url=settings.FIXER_URL, access_key=settings.FIXER_ACCESS_KEY):
        self.base_url = base_url
        self.access_key = access_key

    def get_params(self):
        return {'access_key': self.access_key}
