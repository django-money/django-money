from django.core.exceptions import ImproperlyConfigured

from djmoney import settings

from .base import SimpleExchangeBackend


class UniRateBackend(SimpleExchangeBackend):
    name = "unirateapi.com"

    def __init__(self, url=settings.UNIRATE_URL, access_key=settings.UNIRATE_ACCESS_KEY):
        if access_key is None:
            raise ImproperlyConfigured("settings.UNIRATE_ACCESS_KEY should be set to use UniRateBackend")
        self.url = url
        self.access_key = access_key

    def get_params(self):
        return {"api_key": self.access_key, "from": settings.BASE_CURRENCY}
