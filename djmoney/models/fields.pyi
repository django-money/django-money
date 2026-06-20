from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models.expressions import Combinable

from djmoney.money import Money

class MoneyFieldProxy:
    def __init__(self, field: MoneyField) -> None: ...
    def __get__(self, obj: models.Model | None, type: Any = ...) -> Money | None: ...
    def __set__(self, obj: models.Model, value: Any) -> None: ...

class CurrencyField(models.CharField): ...

class MoneyField(models.DecimalField):
    _pyi_private_set_type: Money | Decimal | float | int | str | Combinable  # type: ignore[assignment]
    _pyi_private_get_type: Money  # type: ignore[assignment]
    _pyi_lookup_exact_type: Money | Decimal | int | str  # type: ignore[assignment]

    def __init__(
        self,
        verbose_name: str | None = ...,
        name: str | None = ...,
        max_digits: int | None = ...,
        decimal_places: int = ...,
        default: Any = ...,
        default_currency: Any = ...,
        currency_choices: Any = ...,
        currency_max_length: int = ...,
        currency_field_name: str | None = ...,
        money_descriptor_class: type[MoneyFieldProxy] = ...,
        **kwargs: Any,
    ) -> None: ...
