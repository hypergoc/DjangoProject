from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Booking


def generate_pdf(request, booking_id):
    booking = Booking.objects.get(pk=booking_id)
    company = booking.apartman.company  # Tvoja firma
    customer = booking.customer

    context = {
        'booking': booking,
        'company': company,
        'customer': customer,
        'services': booking.services.all(),
        'payments': booking.payments.all(),
    }

    html_string = render_to_string('booking/invoice_template.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=racun_{booking.id}.pdf'

    HTML(string=html_string).write_pdf(response)
    return response