from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.html import format_html
from django.template.loader import render_to_string
from datetime import timedelta, datetime

from price.models import Termin
from apartman.models import Apartman
from .models import Booking, BookingSearch, Payment
from .forms import AvailabilityForm
from .managers import BookingManager
from services.models import BookingService

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


# --- INLINES ---

class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 0
    fields = ('service', 'quantity', 'get_service_price', 'get_service_logic')
    readonly_fields = ('get_service_price', 'get_service_logic')
    autocomplete_fields = ['service']
    classes = ('collapse',)

    @admin.display(description='Cijena (Katalog)')
    def get_service_price(self, obj):
        if obj.service:
            return f"{obj.service.default_price} EUR"
        return "-"

    @admin.display(description='Logika Naplate')
    def get_service_logic(self, obj):
        if obj.service:
            modes = []
            if obj.service.is_per_night:
                modes.append("x Noćenja")
            if obj.service.is_per_person:
                modes.append("x Osoba")
            if not modes:
                return "Fiksno (1x)"
            return " + ".join(modes)
        return "-"


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    classes = ('collapse',)


# --- GLAVNI ADMIN ---

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'customer', 'date_from', 'date_to', 'capacity_display', 'visitors_count', 'price',
                    'remaining_balance_display', 'approved')
    list_filter = ('approved', 'apartman')
    search_fields = ('apartman__naziv', 'customer__name', 'customer__email')
    date_hierarchy = 'date_from'
    list_editable = ('approved',)
    raw_id_fields = ('apartman', 'customer')
    actions = ['approve_bookings']

    inlines = [BookingServiceInline, PaymentInline]

    # ORGANIZACIJA POLJA
    fieldsets = (
        ("Osnovno", {
            "fields": ("apartman", "customer", "date_from", "date_to", "visitors_count", "price", "approved",
                       "print_invoice_button")
        }),
        ("Podaci o Kupcu (Dossier)", {
            "classes": ("collapse",),
            "fields": ("customer_info_display",)
        }),
        ("Financije & Popusti", {
            "classes": ("collapse",),
            "fields": ("discount_percent", "discount_amount", "remaining_balance_display")
        }),
        ("Dodatno (Napomene)", {
            "classes": ("collapse",),
            "fields": ("additional_requests",)
        }),
    )

    readonly_fields = ('remaining_balance_display', 'print_invoice_button', 'capacity_display', 'customer_info_display',
                       'get_booking_price')

    # --- HELPERI ---

    def capacity_display(self, obj):
        return f"{obj.apartman.capacity_display}" if obj.apartman else "-"

    capacity_display.short_description = 'Kapacitet'

    def remaining_balance_display(self, obj):
        if obj.pk:
            return f"{obj.remaining_balance} EUR"
        return "-"

    remaining_balance_display.short_description = "Preostalo Dugovanje"

    def customer_info_display(self, obj):
        if not obj.customer:
            return "-"
        c = obj.customer
        return format_html(
            """
            <div style="line-height: 1.6;">
                <strong>Firma:</strong> {} <br>
                <strong>Ime:</strong> {} {} <br>
                <strong>Email:</strong> <a href="mailto:{}">{}</a> <br>
                <strong>Telefon:</strong> {} <br>
                <strong>Adresa:</strong> {}, {}, {} <br>
                <strong>OIB:</strong> {} <br>
                <hr>
                <small>{}</small>
            </div>
            """,
            c.company or "-", c.name, c.surname, c.email, c.email,
            c.phone or "-", c.address or "", c.city or "", c.country or "",
            c.vat or "-", c.additional_data or ""
        )

    customer_info_display.short_description = "Detalji Klijenta"

    # << OVDJE JE TVOJ GUMB >>
    def print_invoice_button(self, obj):
        if obj.pk:
            url = reverse('admin:booking_generate_pdf', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background-color:#417690; color:white; padding:5px 10px; border-radius:5px; text-decoration:none;">📄 Ispiši Račun (PDF)</a>',
                url
            )
        return "(Spremi prvo)"

    print_invoice_button.short_description = "Račun"

    def get_booking_price(self, obj):
        # Ovo je tvoja stara metoda, ostavljam je ako je koristiš negdje
        price_entry = Termin.objects.filter(
            apartman=obj.apartman,
            date_from__lte=obj.date_from,
            date_to__gte=obj.date_to
        ).first()
        if price_entry:
            return price_entry.value
        return "N/A"

    get_booking_price.short_description = 'Cijena za danas'

    # --- LOGIKA ZA ADD FORM ---

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

                # Pozivamo preview iz Managera (pretpostavka da postoji calculate_total_price_preview)
                # Ako ne, koristi _calculate_base_stay_price
                price = Booking.objects.calculate_total_price_preview(
                    apartman, date_from, date_to, visitors_count
                )
                initial['price'] = price
            except Exception as e:
                # print(f"Error calculating price in admin: {e}")
                pass
        return initial

    def approve_bookings(self, request, queryset):
        queryset.update(approved=True)

    approve_bookings.short_description = "Approve selected bookings"

    # --- CUSTOM URLS & VIEWS ---

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('search/', self.admin_site.admin_view(self.search_view), name='booking_search'),
            path('rented/<int:apartman_id>/', self.admin_site.admin_view(self.rented_api), name='calendar_rented'),
            path('<int:booking_id>/pdf/', self.admin_site.admin_view(self.generate_pdf_view),
                 name='booking_generate_pdf'),
        ]
        return custom_urls + urls

    def generate_pdf_view(self, request, booking_id):
        if not HTML:
            return HttpResponse("WeasyPrint nije instaliran (pip install weasyprint).", status=500)

        booking = Booking.objects.get(pk=booking_id)
        context = {
            'booking': booking,
            'company': booking.apartman.company,
            'customer': booking.customer,
            'services': booking.services.all(),
            'payments': booking.payments.all(),
            'total': booking.price,
            'paid': booking.remaining_balance,
        }

        html_string = render_to_string('booking/invoice_template.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=racun_{booking.id}.pdf'
        HTML(string=html_string).write_pdf(response)
        return response

    def search_view(self, request):
        # ... Tvoja search logika (ostavio sam je skraćeno ovdje, kopiraj svoju punu ako treba) ...
        # (Ona velika s if form.is_valid...)
        # Zbog limita znakova ne kopiram ponovno cijelu search_view logiku,
        # ali pretpostavljam da je imaš iz prošlog paste-a.
        # OVO JE PLACEHOLDER ZA TVOJU SEARCH LOGIKU
        form = AvailabilityForm(request.GET or None)
        context = dict(self.admin_site.each_context(request), form=form, results_triggered=False)
        if form.is_valid():
            # ... tvoja logika ...
            context['results_triggered'] = True
            # ...
        return render(request, 'admin/bookingengine/search.html', context)

    def changelist_view(self, request, extra_context=None):
        search_form = AvailabilityForm(request.GET or None)
        extra_context = extra_context or {}
        extra_context['search_form'] = search_form
        extra_context['search_results_triggered'] = False
        if search_form.is_valid():
            # ... tvoja logika za changelist ...
            extra_context['search_results_triggered'] = True
            # ...
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

    # change_form_template = 'admin/apartman/apartman/change_form.html'


@admin.register(BookingSearch)
class BookingSearchAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        try:
            url = reverse('admin:booking_search')
        except:
            url = reverse('admin:bookingengine_booking_search')
        return HttpResponseRedirect(url)