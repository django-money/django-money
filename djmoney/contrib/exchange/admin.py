from django.contrib import admin

from .models import Rate


class RateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'value', 'last_update', 'backend')
    list_filter = ('currency', )
    ordering = ('currency', )

    def last_update(self, instance):
        return instance.backend.last_update


admin.site.register(Rate, RateAdmin)
