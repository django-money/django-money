from django.db.transaction import atomic
from django.utils.http import urlencode

from djmoney._compat import parse_qsl, urlopen, urlparse, urlunparse

from ..models import ExchangeBackend, Rate


class BaseExchangeBackend(object):
    name = None
    base_url = None
    base_currency = None

    def get_rates(self):
        """
        Returns a mapping <currency>: <rate>.
        """
        raise NotImplementedError

    def get_url(self, **params):
        parts = list(urlparse(self.base_url))
        query = dict(parse_qsl(parts[4]))
        query.update(params)
        parts[4] = urlencode(query)
        return urlunparse(parts)

    def get_response(self, **params):
        response = urlopen(self.get_url(**params))
        return response.read()

    @atomic
    def update_rates(self):
        """
        Updates rates for the given backend.
        """
        backend, _ = ExchangeBackend.objects.update_or_create(
            name=self.name, defaults={'base_currency': self.base_currency}
        )
        Rate.objects.all().delete()
        Rate.objects.bulk_create([
            Rate(currency=currency, value=value, backend=backend)
            for currency, value in self.get_rates().items()
        ])
