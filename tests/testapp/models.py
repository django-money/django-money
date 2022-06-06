"""
Created on May 7, 2011

@author: jake
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from djmoney.models.fields import MoneyField
from djmoney.models.managers import money_manager, understands_money
from djmoney.models.validators import MaxMoneyValidator, MinMoneyValidator
from djmoney.money import Money
from moneyed import Money as OldMoney


# Import reversion if configured
if "reversion" in settings.INSTALLED_APPS:
    from reversion.revisions import register
else:
    register = lambda _: None  # noqa


class ModelWithVanillaMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2)
    second_money = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="EUR")
    integer = models.IntegerField(default=0)


class ModelWithNullableCurrency(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency=None)


class ModelWithDefaultAsInt(models.Model):
    money = MoneyField(default=123, max_digits=10, decimal_places=2, default_currency="GHS")


class ModelWithUniqueIdAndCurrency(models.Model):
    money = MoneyField(default=123, max_digits=10, decimal_places=2, default_currency="GHS")

    class Meta:
        unique_together = ("id", "money")


class ModelWithDefaultAsStringWithCurrency(models.Model):
    money = MoneyField(default="123 USD", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "model_default_string_currency"


class ModelWithDefaultAsString(models.Model):
    money = MoneyField(default="123", max_digits=10, decimal_places=2, default_currency="PLN")


class ModelWithDefaultAsFloat(models.Model):
    money = MoneyField(default=12.05, max_digits=10, decimal_places=2, default_currency="PLN")


class ModelWithDefaultAsDecimal(models.Model):
    money = MoneyField(default=Decimal("0.01"), max_digits=10, decimal_places=2, default_currency="CHF")


class ModelWithDefaultAsMoney(models.Model):
    money = MoneyField(default=Money("0.01", "RUB"), max_digits=10, decimal_places=2)


class ModelWithDefaultAsOldMoney(models.Model):
    money = MoneyField(default=OldMoney("0.01", "RUB"), max_digits=10, decimal_places=2)


class ModelWithTwoMoneyFields(models.Model):
    amount1 = MoneyField(max_digits=10, decimal_places=2)
    amount2 = MoneyField(max_digits=10, decimal_places=3)


class ModelRelatedToModelWithMoney(models.Model):
    moneyModel = models.ForeignKey(ModelWithVanillaMoneyField, on_delete=models.CASCADE)


class ModelWithChoicesMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, currency_choices=[("USD", "US Dollars"), ("ZWN", "Zimbabwian")])


class ModelWithNonMoneyField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")
    desc = models.CharField(max_length=10)


class AbstractModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")
    m2m_field = models.ManyToManyField(ModelWithDefaultAsInt)

    class Meta:
        abstract = True


class InheritorModel(AbstractModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")


class RevisionedModel(models.Model):
    amount = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")


register(RevisionedModel)


class BaseModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")


class InheritedModel(BaseModel):
    second_field = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")


class SimpleModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default=0.0, default_currency="USD")


class NullMoneyFieldModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency="USD", blank=True)


class ModelManager(models.Manager):
    pass


class NotNullMoneyFieldModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2)

    objects = money_manager(ModelManager())


class ProxyModelWrapper(NotNullMoneyFieldModel):
    class Meta:
        proxy = True


class ProxyModel(SimpleModel):
    class Meta:
        proxy = True


class MoneyManager(models.Manager):
    @understands_money
    def super_method(self, **kwargs):
        return self.filter(**kwargs)


class ModelWithCustomManager(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2)

    manager = money_manager(MoneyManager())


class DateTimeModel(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(null=True, blank=True)


class ModelIssue300(models.Model):
    money = models.ForeignKey(DateTimeModel, on_delete=models.CASCADE)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency="EUR", default=Decimal("0.0"))


class ModelWithValidation(models.Model):
    balance = MoneyField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Money(100, "GBP"))])


class ModelWithSharedCurrency(models.Model):
    first = MoneyField(max_digits=10, decimal_places=2, currency_field_name="currency")
    second = MoneyField(max_digits=10, decimal_places=2, currency_field_name="currency")


class ValidatedMoneyModel(models.Model):
    money = MoneyField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinMoneyValidator({"EUR": 100, "USD": 50}),
            MaxMoneyValidator({"EUR": 1000, "USD": 500}),
            MinMoneyValidator(Money(500, "NOK")),
            MaxMoneyValidator(Money(900, "NOK")),
            MinMoneyValidator(10),
            MaxMoneyValidator(1500),
        ],
    )


class PositiveValidatedMoneyModel(models.Model):
    """Validated model with a field requiring a non-negative value."""

    money = MoneyField(max_digits=10, decimal_places=2, validators=[MinMoneyValidator(0)])


class ModelWithCustomDefaultManager(models.Model):
    field = MoneyField(max_digits=10, decimal_places=2)

    custom = models.Manager()

    class Meta:
        default_manager_name = "custom"


class CryptoModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, currency_max_length=4)


class PreciseModel(models.Model):
    money = MoneyField(max_digits=10, decimal_places=4)


class ModelWithDefaultPrecision(models.Model):
    money = MoneyField(max_digits=10)


class ModelWithNullDefaultOnNonNullableField(models.Model):
    money = MoneyField(max_digits=10, decimal_places=2, default=None, default_currency=None)
