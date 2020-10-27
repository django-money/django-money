import pytest
from reversion.models import Version
from reversion.revisions import create_revision

from djmoney.money import Money

from .testapp.models import RevisionedModel


@pytest.mark.django_db
def test_that_can_safely_restore_deleted_object():
    amount = Money(100, "GHS")
    with create_revision():
        instance = RevisionedModel.objects.create(amount=amount)
    instance.delete()
    version = Version.objects.get_deleted(RevisionedModel)[0]
    version.revision.revert()
    instance = RevisionedModel.objects.get(pk=1)
    assert instance.amount == amount
