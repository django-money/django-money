from django.test import TestCase
from django.db.models import Q
from djmoney.models.managers import _expand_money_args
from djmoney.tests.testapp.models import ModelWithNonMoneyField
from moneyed import Money


class ExpandMoneyArgsTestCase(TestCase):

    def testExpandMoneyArgs(self):
        # Test no args
        self.assertEqual(
            _expand_money_args(ModelWithNonMoneyField(), []),
            []
        )

        # Test non-Q arg (such as it receives for an order_by
        self.assertEqual(
            _expand_money_args(ModelWithNonMoneyField(), ['money']),
            ['money']
        )

        # Test
        #   (AND: ('money', 0 USD))
        # results in;
        #   (AND: (AND: ('money', 0 USD), ('money_currency', u'USD')))
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'))])

        self.assertEqual(len(actual), 1)
        arg = actual[0]

        self.assertIsInstance(arg, Q)
        self.assertEqual(arg.connector, Q.AND)
        self.assertEqual(len(arg.children), 1)
        self.assertIsInstance(arg.children[0], Q)
        self.assertEqual(arg.children[0].connector, Q.AND)
        self.assertIn(('money', Money(0, 'USD')), arg.children[0].children)
        self.assertIn(('money_currency', 'USD'), arg.children[0].children)

        # Test
        #   (AND: ('desc', 'foo'), ('money', 0 USD))
        # results in;
        #   (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD')))
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'), desc='foo')])
        self.assertEqual(len(actual), 1)

        arg = actual[0]

        self.assertIsInstance(arg, Q)
        self.assertEqual(arg.connector, Q.AND)
        self.assertEqual(len(arg.children), 2)

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                self.assertEqual(('desc', 'foo'), child)
            elif isinstance(child, Q):
                self.assertEqual(child.connector, Q.AND)
                self.assertEqual(len(child.children), 2)
                self.assertIn(('money', Money(0, 'USD')), child.children)
                self.assertIn(('money_currency', 'USD'), child.children)
            else:
                self.fail("There should only be two elements, a tuple and a Q - not a %s" % child)

        # Test
        #   (OR: (AND: ('desc', 'foo'), ('money', 0 USD)), ('desc', 'bar'))
        # results in:
        #   (OR: (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD'))), ('desc', 'bar'))
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'), desc='foo') | Q(desc='bar')])

        self.assertEqual(len(actual), 1)
        arg = actual[0]

        self.assertIsInstance(arg, Q)
        self.assertEqual(arg.connector, Q.OR)
        self.assertEqual(len(arg.children), 2)

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                self.assertEqual(('desc', 'bar'), child)
            elif isinstance(child, Q):
                self.assertEqual(len(child.children), 2)
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        self.assertEqual(('desc', 'foo'), subchild)
                    elif isinstance(subchild, Q):
                        self.assertIn(('money', Money(0, 'USD')), subchild.children)
                        self.assertIn(('money_currency', 'USD'), subchild.children)
            else:
                self.fail("There should only be two elements, a tuple and a Q - not a %s" % child)

        # Test
        #   (OR: (OR: (AND: ('desc', 'foo'), ('money', 0 USD)), ('desc', 'eggs')), ('desc', 'bar'))
        # results in;
        #   (OR: (OR: (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD'))), ('desc', 'eggs')), ('desc', 'bar'))
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(Q(money=Money(0, 'USD'), desc='foo') | Q(desc='eggs')) | Q(desc='bar')])
        arg = actual[0]

        self.assertEqual(len(actual), 1)
        self.assertIsInstance(arg, Q)
        self.assertEqual(arg.connector, Q.OR)
        self.assertEqual(len(arg.children), 2)

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                self.assertEqual(('desc', 'bar'), child)
            elif isinstance(child, Q):
                self.assertEqual(len(child.children), 2)
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        self.assertEqual(('desc', 'eggs'), subchild)
                    elif isinstance(subchild, Q):
                        for subsubchild in subchild.children:
                            if isinstance(subsubchild, tuple):
                                self.assertEqual(('desc', 'foo'), subsubchild)
                            elif isinstance(subsubchild, Q):
                                self.assertIn(('money', Money(0, 'USD')), subsubchild.children)
                                self.assertIn(('money_currency', 'USD'), subsubchild.children)
                            else:
                                self.fail("There should only be two subsubchild elements, a tuple and a Q - not a %s" % subsubchild)
                    else:
                        self.fail("There should only be two subchild elements, a tuple and a Q - not a %s" % subsubchild)
            else:
                self.fail("There should only be two child elements, a tuple and a Q - not a %s" % child)
