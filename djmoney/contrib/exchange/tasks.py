from django.utils.module_loading import import_string

from celery import shared_task
from djmoney import settings


@shared_task
def update_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
    backend = import_string(backend)()
    backend.update_rates(**kwargs)
