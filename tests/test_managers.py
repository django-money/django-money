from django.db.models import F, Q

import pytest

from djmoney.models.managers import _expand_money_args, _expand_money_kwargs
from djmoney.money import Money
from djmoney.utils import get_amount
from moneyed import Money as OldMoney

from .testapp.models import ModelWithNonMoneyField


def assert_leafs(children):
    assert ("money", Money(0, "USD")) in children
    assert ("money_currency", "USD") in children


class TestExpandMoneyArgs:
    def test_no_args(self):
        assert _expand_money_args(ModelWithNonMoneyField(), []) == []

    def test_non_q_args(self):
        assert _expand_money_args(ModelWithNonMoneyField(), ["money"]) == ["money"]

    def test_exact(self):
        """
        Test
          (AND: ('money', 0 USD))
        results in;
          (AND: (AND: ('money', 0 USD), ('money_currency', u'USD')))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, "USD"))])

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
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, "USD"), desc="foo")])

        assert len(actual) == 1
        arg = actual[0]

        assert isinstance(arg, Q)
        assert arg.connector == Q.AND
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ("desc", "foo") == child
            elif isinstance(child, Q):
                assert child.connector == Q.AND
                assert len(child.children) == 2
                assert_leafs(child.children)
            else:
                pytest.fail("There should only be two elements, a tuple and a Q - not a %s" % child)

    def test_and_with_or(self):
        """
        Test
          (OR: (AND: ('desc', 'foo'), ('money', 0 USD)), ('desc', 'bar'))
        results in:
          (OR: (AND: ('desc', 'foo'), (AND: ('money', 0 USD), ('money_currency', u'USD'))), ('desc', 'bar'))
        """
        actual = _expand_money_args(ModelWithNonMoneyField(), [Q(money=Money(0, "USD"), desc="foo") | Q(desc="bar")])

        assert len(actual) == 1
        arg = actual[0]

        assert isinstance(arg, Q)
        assert arg.connector == Q.OR
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ("desc", "bar") == child
            elif isinstance(child, Q):
                assert len(child.children) == 2
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        assert ("desc", "foo") == subchild
                    elif isinstance(subchild, Q):
                        assert_leafs(subchild.children)
            else:
                pytest.fail("There should only be two elements, a tuple and a Q - not a %s" % child)

    def test_and_with_two_or(self):
        """
        Test
          (OR:
            (OR:
              (AND:
                ('desc', 'foo'),
                ('money', 0 USD)
              ),
              ('desc', 'eggs')
            ),
            ('desc', 'bar')
          )
        results in;
          (OR:
            (OR:
              (AND:
                ('desc', 'foo'),
                (AND:
                  ('money', 0),
                  ('money_currency', 'USD')
                )
              ),
              ('desc', 'eggs')
            ),
            ('desc', 'bar')
          )
        """
        actual = _expand_money_args(
            ModelWithNonMoneyField(), [Q(Q(money=Money(0, "USD"), desc="foo") | Q(desc="eggs")) | Q(desc="bar")]
        )
        arg = actual[0]

        assert len(actual) == 1
        assert isinstance(arg, Q)
        assert arg.connector == Q.OR
        assert len(arg.children) == 2

        # Can't guarantee the ordering of children, thus;
        for child in arg.children:
            if isinstance(child, tuple):
                assert ("desc", "bar") == child
            elif isinstance(child, Q):
                assert len(child.children) == 2
                for subchild in child.children:
                    if isinstance(subchild, tuple):
                        assert ("desc", "eggs") == subchild
                    elif isinstance(subchild, Q):
                        for subsubchild in subchild.children:
                            if isinstance(subsubchild, tuple):
                                assert ("desc", "foo") == subsubchild
                            elif isinstance(subsubchild, Q):
                                assert_leafs(subsubchild.children)
                            else:
                                pytest.fail(
                                    "There should only be two subsubchild elements, a tuple and a Q - not a %s"
                                    % subsubchild
                                )
                    else:
                        pytest.fail(
                            "There should only be two subchild elements, a tuple and a Q - not a %s" % subsubchild
                        )
            else:
                pytest.fail("There should only be two child elements, a tuple and a Q - not a %s" % child)


class TestKwargsExpand:
    @pytest.mark.parametrize(
        "value, expected",
        (
            (
                ({"money": 100, "desc": "test"}, {"money": 100, "desc": "test"}),
                ({"money": Money(100, "USD")}, {"money": 100, "money_currency": "USD"}),
                ({"money": OldMoney(100, "USD")}, {"money": 100, "money_currency": "USD"}),
                ({"money": Money(100, "USD"), "desc": "test"}, {"money": 100, "money_currency": "USD", "desc": "test"}),
            )
        ),
    )
    def test_simple(self, value, expected):
        assert _expand_money_kwargs(ModelWithNonMoneyField, kwargs=value)[1] == expected

    @pytest.mark.parametrize(
        "value, expected", (({"money": F("money") * 2}, 2), ({"money": F("money") + Money(100, "USD")}, 100))
    )
    def test_complex_f_query(self, value, expected):
        _, kwargs = _expand_money_kwargs(ModelWithNonMoneyField, kwargs=value)
        assert isinstance(kwargs["money_currency"], F)
        assert kwargs["money_currency"].name == "money_currency"
        assert get_amount(kwargs["money"].rhs) == expected

    def test_simple_f_query(self):
        _, kwargs = _expand_money_kwargs(ModelWithNonMoneyField, kwargs={"money": F("money")})
        assert isinstance(kwargs["money_currency"], F)
        assert kwargs["money_currency"].name == "money_currency"
        assert kwargs["money"].name == "money"
