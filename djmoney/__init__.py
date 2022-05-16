import django

__version__ = "2.1.1"

if django.VERSION >= (3, 2):
    # The declaration is only needed for older Django versions
    pass
else:
    default_app_config = "djmoney.apps.MoneyConfig"

