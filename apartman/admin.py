
### apartman/admin.py

from django.contrib import admin
from .models import Apartman
from price.models import Termin
from datetime import date

@admin.register(Apartman)
class ApartmanAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'company', 'size', 'capacity', 'get_todays_price')
    search_fields = ('naziv', 'company__name', 'opis')
    list_filter = ('company',)
    # raw_id_fields is useful for ForeignKey fields with many options
    raw_id_fields = ('company',)

    def get_todays_price(self, obj):
        """
        Dohvaća cijenu za apartman za današnji dan iz Price modela.
        """
        today = date.today()



        price_entry = Termin.objects.filter(apartman=obj, date_from__lte = today, date_to__gte=today).first()
        if price_entry:
            return price_entry.value
        return "N/A"

    get_todays_price.short_description = 'Cijena za danas'
