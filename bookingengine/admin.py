from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from price.models import Termin
from apartman.models import Apartman
from .models import Booking, BookingSearch
from .forms import AvailabilityForm

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'customer', 'date_from', 'date_to', 'visitors_count', 'approved', 'created_at')
    list_filter = ('approved', 'apartman')
    search_fields = ('apartman__naziv', 'customer__name', 'customer__email') # Adjust customer fields as needed
    date_hierarchy = 'date_from'
    list_editable = ('approved',)
    raw_id_fields = ('apartman', 'customer')

    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(approved=True)
    approve_bookings.short_description = "Approve selected bookings"

    def get_booking_price(self, obj):


        price_entry = Termin.objects.filter(apartman=obj, date_from__lte = obj.date_from, date_to__gte=obj.date).first()
        if price_entry:
            return price_entry.value
        return "N/A"

    get_booking_price.short_description = 'Cijena za danas'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('search/', self.admin_site.admin_view(self.search_view), name='booking_search'),
        ]
        return custom_urls + urls

    # << OVO JE MOZAK NAŠE NOVE STRANICE >>
    def search_view(self, request):
        """Ovaj view kontrolira našu custom admin stranicu."""
        form = AvailabilityForm(request.GET or None)
        context = dict(
            # Ovo su varijable potrebne da Django Admin prikaže stranicu ispravno
            self.admin_site.each_context(request),
            form=form,
            results_triggered=False  # Zastavica da znamo je li pretraga pokrenuta
        )

        if form.is_valid():
            context['results_triggered'] = True
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            capacity = form.cleaned_data['capacity']

            # Isti onaj sveti query od prije
            overlapping_bookings = Booking.objects.filter(
                date_from__lt=date_to,
                date_to__gt=date_from
            ).values_list('apartman_id', flat=True)

            available_apartments = Apartman.objects.exclude(
                pk__in=overlapping_bookings
            ).filter(
                capacity__gte=capacity
            )
            context['apartmani'] = available_apartments
            context['date_from'] = date_from
            context['date_to'] = date_to
            context['capacity'] = capacity


        return render(request, 'admin/bookingengine/search.html', context)

    def changelist_view(self, request, extra_context=None):
        """
        Pregazimo defaultni changelist view da bismo dodali našu logiku.
        """
        # Inicijaliziramo formu s podacima iz GET requesta
        search_form = AvailabilityForm(request.GET or None)

        # Pripremamo defaultni kontekst, dodajemo mu našu formu
        extra_context = extra_context or {}
        extra_context['search_form'] = search_form
        extra_context['search_results_triggered'] = False

        if search_form.is_valid():
            # Ako je forma ispravna, radi istu logiku kao i prije...
            extra_context['search_results_triggered'] = True
            date_from = search_form.cleaned_data['date_from']
            date_to = search_form.cleaned_data['date_to']
            capacity = search_form.cleaned_data['capacity']

            overlapping_bookings = Booking.objects.filter(
                date_from__lt=date_to,
                date_to__gt=date_from
            ).values_list('apartman_id', flat=True)

            available_apartments = Apartman.objects.exclude(
                pk__in=overlapping_bookings
            ).filter(
                capacity__gte=capacity
            )
            extra_context['available_apartments'] = available_apartments

        # Na kraju, pozivamo originalnu metodu da odradi svoj posao, ali
        # joj prosljeđujemo naš obogaćeni kontekst!
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(BookingSearch)
class BookingSearchAdmin(admin.ModelAdmin):

    # Ova funkcija se izvršava kada korisnik klikne na "Search" u meniju
    def changelist_view(self, request, extra_context=None):
        try:
            url = reverse('admin:booking_search')
        except:
            url = reverse('admin:bookingengine_booking_search')

        return HttpResponseRedirect(url)