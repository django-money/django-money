# coding=utf-8
from django.db.models import Q

import pytest
from moneyed import Money

from djmoney.models.managers import _expand_money_args

from .testapp.models import ModelWithNonMoneyField


def assert_leafs(children):
    assert ('money', Money(0, 'USD')) in children
    assert ('money_currency', 'USD') in children


class TestExpandMoneyArgs:

    def test_no_args(self):
        assert _expand_money_args(ModelWithNonMoneyField(), []) == []

    def test_non_q_args(self):
        assert _expand_money_args(ModelWithNonMoneyField(), ['money']) == ['money']

    def test_exact(self):
        """
        Test
          (AND: ('money', 0 USD))
        results in;
          (AND: (AND: ('money', 0 USD), ('money_currency', u'USD')))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'))])

        assert len(actual) == 1
        arg = actual[0]

        assert isinstance(arg, Q)
        assert arg.connector == Q.AND
        assert len(arg.children) == 1
        assert isinstance(arg.children[0], Q)
        assert arg.children[0].connector == Q.AND
        assert_leafs(arg.children[0].children)

    def test_and(self):
        """
        Test
          (AND: ('desc', 'foo'), ('money', 0 USD))
        results in;
          (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD')))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'), desc='foo')])

        assert len(actual) == 1
        arg = actual[0]

        assert isinstance(arg, Q)
        assert arg.connector == Q.AND
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ('desc', 'foo') == child
            elif isinstance(child, Q):
                assert child.connector == Q.AND
                assert len(child.children) == 2
                assert_leafs(child.children)
            else:
                pytest.fail('There should only be two elements, a tuple and a Q - not a %s' % child)

    def test_and_with_or(self):
        """
        Test
          (OR: (AND: ('desc', 'foo'), ('money', 0 USD)), ('desc', 'bar'))
        results in:
          (OR: (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD'))), ('desc', 'bar'))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, 'USD'), desc='foo') | Q(desc='bar')])

        assert len(actual) == 1
        arg = actual[0]

        assert isinstance(arg, Q)
        assert arg.connector == Q.OR
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ('desc', 'bar') == child
            elif isinstance(child, Q):
                assert len(child.children) == 2
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        assert ('desc', 'foo') == subchild
                    elif isinstance(subchild, Q):
                        assert_leafs(subchild.children)
            else:
                pytest.fail("There should only be two elements, a tuple and a Q - not a %s" % child)

    def test_and_with_two_or(self):
        """
        Test
          (OR: (OR: (AND: ('desc', 'foo'), ('money', 0 USD)), ('desc', 'eggs')), ('desc', 'bar'))
        results in;
          (OR: (OR: (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD'))), ('desc', 'eggs')), ('desc', 'bar'))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(Q(money=Money(0, 'USD'), desc='foo') | Q(desc='eggs')) | Q(desc='bar')])
        arg = actual[0]

        assert len(actual) == 1
        assert isinstance(arg, Q)
        assert arg.connector == Q.OR
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ('desc', 'bar') == child
            elif isinstance(child, Q):
                assert len(child.children) == 2
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        assert ('desc', 'eggs') == subchild
                    elif isinstance(subchild, Q):
                        for subsubchild in subchild.children:
                            if isinstance(subsubchild, tuple):
                                assert ('desc', 'foo') == subsubchild
                            elif isinstance(subsubchild, Q):
                                assert_leafs(subsubchild.children)
                            else:
                                pytest.fail('There should only be two subsubchild elements, a tuple and a Q - not a %s' % subsubchild)
                    else:
                        pytest.fail('There should only be two subchild elements, a tuple and a Q - not a %s' % subsubchild)
            else:
                pytest.fail('There should only be two child elements, a tuple and a Q - not a %s' % child)
