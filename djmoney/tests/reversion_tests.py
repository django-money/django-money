from django.test import TestCase
from testapp.models import RevisionedModel
from moneyed import Money
import reversion


class ReversionTestCase(TestCase):
    def test_that_can_safely_restore_deleted_object(self):
        model = None
        amount = Money(100, 'GHS')
        with reversion.create_revision():
            model = RevisionedModel.objects.create(amount=amount)
            model.save()
        model.delete()
        version = reversion.get_deleted(RevisionedModel)[0]
        version.revision.revert()
        model = RevisionedModel.objects.get(pk=1)
        self.assertEquals(model.amount, amount)
