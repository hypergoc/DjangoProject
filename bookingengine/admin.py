from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from price.models import Termin
from apartman.models import Apartman
from .models import Booking, BookingSearch
from .forms import AvailabilityForm
from datetime import timedelta
from django.http import JsonResponse
from datetime import datetime
from .managers import BookingManager

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'customer', 'date_from', 'date_to', 'capacity_display', 'visitors_count', 'approved', 'price')
    list_filter = ('approved', 'apartman')
    search_fields = ('apartman__naziv', 'customer__name', 'customer__email') # Adjust customer fields as needed
    date_hierarchy = 'date_from'
    list_editable = ('approved',)
    raw_id_fields = ('apartman', 'customer')

    actions = ['approve_bookings']

    def capacity_display(self, obj):
        return f"{obj.apartman.capacity_display}"

    capacity_display.short_description = 'Kapacitet'

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        apartman_id = request.GET.get('apartman')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')

        # Ovdje samo prenosimo podatke
        initial['apartman'] = apartman_id
        initial['date_from'] = date_from_str
        initial['date_to'] = date_to_str
        initial['visitors_count'] = request.GET.get('visitors_count')

        print(initial)

        # << NOVA MAGIJA >>
        # Ako imamo SVE podatke, pozovimo našu centralnu logiku!
        if apartman_id and date_from_str and date_to_str:
            try:
                apartman = Apartman.objects.get(pk=apartman_id)
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
                price = Booking.objects.calculate_price_for_period(apartman=apartman, date_from=date_from, date_to=date_to)
                initial['price'] = price
            except (ValueError, Apartman.DoesNotExist, Exception):
                # Ako ne uspije (npr. ne nađe cijenu), samo nemoj postaviti initial cijenu
                # Save metoda će svejedno dignuti grešku ako je potrebno
                pass

        return initial

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
            path('rented/<int:apartman_id>/', self.admin_site.admin_view(self.rented_api), name='calendar_rented'),
        ]
        return custom_urls + urls

    # << OVO JE MOZAK NAŠE NOVE STRANICE >>
    def search_view(self, request):
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

            # ... (ista logika za overlapping_bookings i available_apartments) ...
            overlapping_bookings_ids = Booking.objects.filter(
                date_from__lt=date_to,
                date_to__gt=date_from
            ).values_list('apartman_id', flat=True)

            available_apartments = Apartman.objects.exclude(
                pk__in=overlapping_bookings_ids
            )
            if capacity:
                available_apartments = available_apartments.filter(capacity__gte=capacity)

            # << OVDJE JE NOVA MAGIJA >>
            if available_apartments.exists():
                # Ako ima slobodnih, prikaži ih
                context['apartmani'] = available_apartments
            else:
                # AKO NEMA, pokreni Plan B!
                context['showing_conflicts'] = True

                # Definiramo širi prozor za prikaz zauzeća
                start_window = date_from - timedelta(days=15)
                end_window = date_from + timedelta(days=15)

                # Dohvaćamo SVE bookinge u tom širem prozoru
                conflicting_bookings = Booking.objects.filter(
                    date_from__lt=end_window,
                    date_to__gt=start_window
                ).order_by('date_from') # Sortiramo da bude preglednije

                context['conflicting_bookings'] = conflicting_bookings
                context['search_window_start'] = start_window
                context['search_window_end'] = end_window

            context['date_from'] = date_from
            context['date_to'] = date_to
            context['capacity'] = capacity
        return render(request, 'admin/bookingengine/search.html', context)

    def changelist_view(self, request, extra_context=None):
        search_form = AvailabilityForm(request.GET or None)
        extra_context = extra_context or {}
        extra_context['search_form'] = search_form
        extra_context['search_results_triggered'] = False

        if search_form.is_valid():
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

        return super().changelist_view(request, extra_context=extra_context)

    def rented_api(self, request, apartman_id):
        try:
            # bookings = Booking.objects.filter(apartman_id=apartman_id, approved=True)
            bookings = Booking.objects.filter(apartman_id=apartman_id,)

            formatted_events = []
            for booking in bookings:
                formatted_events.append({
                    'start': booking.date_from,
                    'end': booking.date_to,
                    'color': '#dc3545',
                    'display': 'background'
                })
            return JsonResponse(formatted_events, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@admin.register(BookingSearch)
class BookingSearchAdmin(admin.ModelAdmin):

    # Ova funkcija se izvršava kada korisnik klikne na "Search" u meniju
    def changelist_view(self, request, extra_context=None):
        try:
            url = reverse('admin:booking_search')
        except:
            url = reverse('admin:bookingengine_booking_search')

        return HttpResponseRedirect(url)