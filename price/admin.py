from django.contrib import admin
from .models import Termin

@admin.register(Termin)
class TerminAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'date_from', 'date_to', 'value')
    list_filter = ('apartman',)
    search_fields = ('apartman__naziv',)
    date_hierarchy = 'date_from'
    raw_id_fields = ('apartman',)