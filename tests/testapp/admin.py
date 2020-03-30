from django.contrib import admin

from .models import InheritedModel


class InheritedModelAdmin(admin.ModelAdmin):
    readonly_fields = ("second_field",)


admin.site.register(InheritedModel, InheritedModelAdmin)
