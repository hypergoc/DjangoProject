from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Booking
from .forms import BookingForm

class BookingListView(ListView):
    model = Booking
    template_name = 'bookingengine/booking_list.html'
    context_object_name = 'bookings'

class BookingDetailView(DetailView):
    model = Booking
    template_name = 'bookingengine/booking_detail.html'
    context_object_name = 'booking'

class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookingengine/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookingengine/booking_form.html'
    success_url = reverse_lazy('booking_list')

class BookingDeleteView(DeleteView):
    model = Booking
    template_name = 'bookingengine/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')