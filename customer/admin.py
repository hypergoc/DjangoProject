from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'surname', 'email', 'phone', 'city', 'country', 'vat')
    list_filter = ('city', 'country')
    search_fields = ('company', 'name', 'surname', 'email', 'vat')
    fieldsets = (
        (None, {
            'fields': ('company', 'name', 'surname', 'email', 'vat', 'discount_percent')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'country')
        }),
        ('Additional Information', {
            'fields': ('additional_data',),
            'classes': ('collapse',)
        }),
    )