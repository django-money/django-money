# coding=utf-8
import pytest
from moneyed import Money

from ._compat import reversion
from .testapp.models import RevisionedModel


@pytest.mark.django_db
def test_that_can_safely_restore_deleted_object():
    amount = Money(100, 'GHS')
    with reversion.create_revision():
        instance = RevisionedModel.objects.create(amount=amount)
    instance.delete()
    version = reversion.get_deleted(RevisionedModel)[0]
    version.revision.revert()
    instance = RevisionedModel.objects.get(pk=1)
    assert instance.amount == amount
