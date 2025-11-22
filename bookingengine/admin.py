from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import JsonResponse
from datetime import timedelta, datetime
from price.models import Termin
from apartman.models import Apartman
from .models import Booking, BookingSearch
from .forms import AvailabilityForm
from .managers import BookingManager
from services.models import BookingService

# 1. Definiraj Inline
class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 0

    # Ažuriraj imena polja!
    fields = ('service', 'quantity')

    # OVDJE JE GREŠKA BILA:
    autocomplete_fields = ['service']  # Bilo je 'definition'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'customer', 'date_from', 'date_to', 'capacity_display', 'visitors_count', 'approved',
                    'price')
    list_filter = ('approved', 'apartman')
    search_fields = ('apartman__naziv', 'customer__name', 'customer__email')
    date_hierarchy = 'date_from'
    list_editable = ('approved',)
    raw_id_fields = ('apartman', 'customer')

    inlines = [BookingServiceInline]

    actions = ['approve_bookings']




    def capacity_display(self, obj):
        return f"{obj.apartman.capacity_display}"

    capacity_display.short_description = 'Kapacitet'

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        apartman_id = request.GET.get('apartman')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        visitors_count_str = request.GET.get('visitors_count')

        initial['apartman'] = apartman_id
        initial['date_from'] = date_from_str
        initial['date_to'] = date_to_str
        initial['visitors_count'] = visitors_count_str

        if apartman_id and date_from_str and date_to_str:
            try:
                apartman = Apartman.objects.get(pk=apartman_id)
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
                visitors_count = int(visitors_count_str) if visitors_count_str else 1

                # Ovdje pozivamo preview metodu jer nemamo instancu bookinga
                # Provjeri da li je imas u Manageru, ako ne, koristi calculate_base_stay_price
                # ili dodaj logiku ovdje privremeno.
                # Ovdje koristim pretpostavku da si dodao calculate_total_price_preview
                price = Booking.objects.calculate_total_price_preview(
                    apartman, date_from, date_to, visitors_count
                )
                initial['price'] = price
            except Exception as e:
                print(f"Error calculating price in admin: {e}")
                pass

        return initial

    def approve_bookings(self, request, queryset):
        queryset.update(approved=True)

    approve_bookings.short_description = "Approve selected bookings"

    def get_booking_price(self, obj):
        price_entry = Termin.objects.filter(
            apartman=obj.apartman,
            date_from__lte=obj.date_from,
            date_to__gte=obj.date_to
        ).first()
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

    def search_view(self, request):
        form = AvailabilityForm(request.GET or None)
        context = dict(
            self.admin_site.each_context(request),
            form=form,
            results_triggered=False
        )

        if form.is_valid():
            context['results_triggered'] = True
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            capacity = form.cleaned_data['capacity']

            overlapping_bookings_ids = Booking.objects.filter(
                date_from__lt=date_to,
                date_to__gt=date_from
            ).values_list('apartman_id', flat=True)

            available_apartments = Apartman.objects.exclude(
                pk__in=overlapping_bookings_ids
            )
            if capacity:
                available_apartments = available_apartments.filter(capacity__gte=capacity)

            if available_apartments.exists():
                context['apartmani'] = available_apartments
            else:
                context['showing_conflicts'] = True
                start_window = date_from - timedelta(days=15)
                end_window = date_from + timedelta(days=15)

                conflicting_bookings = Booking.objects.filter(
                    date_from__lt=end_window,
                    date_to__gt=start_window
                ).order_by('date_from')

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
            bookings = Booking.objects.filter(apartman_id=apartman_id)
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
    def changelist_view(self, request, extra_context=None):
        try:
            url = reverse('admin:booking_search')
        except:
            url = reverse('admin:bookingengine_booking_search')
        return HttpResponseRedirect(url)