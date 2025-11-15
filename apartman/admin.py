
### apartman/admin.py

from django.contrib import admin
from .models import Apartman
from price.models import Termin
from bookingengine.models import Booking
from datetime import date

class TerminInline(admin.TabularInline):
    model = Termin
    fields = ('date_from', 'date_to', 'value')
    extra = 1
    ordering = ('date_from',)

class BookingInline(admin.TabularInline):
    model = Booking
    fields = ('date_from', 'date_to', 'price', 'visitors_count', 'approved')
    extra = 1
    ordering = ('date_from',)

@admin.register(Apartman)
class ApartmanAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'company', 'size', 'capacity', 'get_todays_price')
    search_fields = ('naziv', 'company__name', 'opis')
    list_filter = ('company',)
    raw_id_fields = ('company',)
    inlines = [TerminInline, BookingInline]

    def get_todays_price(self, obj):
        today = date.today()
        price_entry = Termin.objects.filter(apartman=obj, date_from__lte = today, date_to__gte=today).first()
        if price_entry:
            return price_entry.value
        return "N/A"
    get_todays_price.short_description = 'Cijena za danas'
