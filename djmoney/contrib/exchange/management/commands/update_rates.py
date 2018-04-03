from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from djmoney import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-b', '--backend',
            action='store',
            dest='backend',
            help='Importable string for custom exchange rates backend.',
            required=False,
            default=settings.EXCHANGE_BACKEND,
        )

    def handle(self, *args, **options):
        backend = import_string(options['backend'])()
        backend.update_rates()
