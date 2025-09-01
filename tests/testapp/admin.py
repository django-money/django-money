from django.contrib import admin

from .models import InheritedModel, ModelWithParentAndCallableFields, ParentModel


class ItemAdmin(admin.TabularInline):
    model = ModelWithParentAndCallableFields
    fields = ["money"]
    extra = 1
    max_num = 2


@admin.register(InheritedModel)
class InheritedModelAdmin(admin.ModelAdmin):
    readonly_fields = ("second_field",)


@admin.register(ParentModel)
class ParentModelAdmin(admin.ModelAdmin):
    inlines = [ItemAdmin]
