from django.forms import HiddenInput, MultiWidget, Select, TextInput

from ..settings import CURRENCY_CHOICES


__all__ = (
    "HiddenMoneyWidget",
    "MoneyWidget",
)


class HiddenMoneyWidget(HiddenInput):

    def format_value(self, value):
        if value is None:
            return ""
        # For hidden inputs, we are sometimes supplied with a pre-formatted value
        if isinstance(value, str):
            return value
        # The hidden input widget is used in a MultiField (MoneyField!)
        if isinstance(value, list):
            amount, currency = value
            return f"{amount} {currency}"
        # Assuming it's a money object
        return f"{value.amount} {value.currency}"


class MoneyWidget(MultiWidget):
    def __init__(
        self,
        choices=CURRENCY_CHOICES,
        amount_widget=TextInput,
        currency_widget=None,
        default_currency=None,
        *args,
        **kwargs,
    ):
        self.default_currency = default_currency
        if not currency_widget:
            currency_widget = Select(choices=choices)
        widgets = (amount_widget, currency_widget)
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is not None:
            # Value provided by hidden input submissions somehow being evaluated in this widget
            # TBD: Why does that happen when MoneyField.hidden_widget() is defined?
            if isinstance(value, str):
                if " " in value:
                    amount, currency = value.split(" ")
                    return [amount, currency]
                raise ValueError(f"Invalid money value: {value}")
            if isinstance(value, (list, tuple)):
                return value
            elif isinstance(value, str):
                return (
                    value.split(',') + [self.default_currency])[:2]
            return [value.amount, value.currency]
        return [None, self.default_currency]
