from django.contrib import admin
from .models import Apartman

@admin.register(Apartman)
class ApartmanAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'company', 'size', 'capacity')
    search_fields = ('naziv', 'company__name', 'opis')
    list_filter = ('company',)
    # raw_id_fields is useful for ForeignKey fields with many options
    raw_id_fields = ('company',)