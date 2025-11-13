from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone', 'city', 'country')
    search_fields = ('name', 'surname', 'email', 'vat')
    list_filter = ('country', 'city')