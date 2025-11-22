from django.contrib import admin
from .models import BookingService, Service
from bookingengine.models import Booking

# from services.models import BookingService

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'default_price', 'calculation_logic', 'is_global_default')
    list_filter = ('is_per_night', 'is_per_person', 'is_global_default')
    search_fields = ('title',)
    list_editable = ('default_price', 'is_global_default')  # Brzo mijenjanje cijena direktno iz liste

    # Helper metoda da lijepo ispiše logiku u tablici
    @admin.display(description='Logika naplate')
    def calculation_logic(self, obj):
        modes = []
        if obj.is_per_night:
            modes.append("x Noćenja")
        if obj.is_per_person:
            modes.append("x Osoba/Kom")

        if not modes:
            return "Fiksno (Jednokratno)"
        return " + ".join(modes)

    # Malo šminke za fieldsetove da bude uredno kod unosa
    fieldsets = (
        ("Osnovno", {
            "fields": ("title", "default_price", "is_global_default")
        }),
        ("Logika Obračuna", {
            "fields": ("is_per_night", "is_per_person"),
            "description": "Odaberi kako se ova usluga množi."
        }),
    )

class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 1  # Daje ti jedan prazan red za dodavanje
    fields = ('name', 'price', 'quantity', 'is_per_night')
    # Ovdje bi bilo super imati neki JS koji kad odabereš definiciju, popuni polja.
    # Ali za početak, ručni unos ili custom forma.


class BookingAdmin(admin.ModelAdmin):
    inlines = [BookingServiceInline]  # Dodajemo inline

    # ... tvoja get_changeform_initial_data logika ...

    def save_model(self, request, obj, form, change):
        # Ovdje možemo (ako je novi booking) automatski kreirati
        # one servise koji imaju is_global_default=True
        super().save_model(request, obj, form, change)

        if not change:  # Samo kod kreiranja
            defaults = Service.objects.filter(is_global_default=True)
            for d in defaults:
                BookingService.objects.create(
                    booking=obj,
                    name=d.title,
                    price=d.default_price,
                    is_per_night=d.is_per_night,
                    definition=d
                )
