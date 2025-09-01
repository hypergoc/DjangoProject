from django.contrib import admin
from .models import Setting

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('path', 'value', 'default')
    search_fields = ('path', 'value')
    list_filter = ('default',)
    ordering = ('path',)