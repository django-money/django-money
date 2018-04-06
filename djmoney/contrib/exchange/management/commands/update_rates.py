from django.utils.module_loading import import_string

from ..base import BaseExchangeCommand


class Command(BaseExchangeCommand):
    help = 'Updates exchange rates.'

    def handle(self, *args, **options):
        backend = import_string(options['backend'])()
        backend.update_rates()
