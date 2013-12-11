from django.contrib import admin

import models

class InheritedModelAdmin(admin.ModelAdmin):
     readonly_fields = ('second_field',)

admin.site.register(models.InheritedModel, InheritedModelAdmin)
