from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Termin
from .forms import TerminForm

class TerminListView(ListView):
    model = Termin
    template_name = 'price/termin_list.html'
    context_object_name = 'termini'

class TerminDetailView(DetailView):
    model = Termin
    template_name = 'price/termin_detail.html'
    context_object_name = 'termin'

class TerminCreateView(CreateView):
    model = Termin
    form_class = TerminForm
    template_name = 'price/termin_form.html'
    success_url = reverse_lazy('termin_list')

class TerminUpdateView(UpdateView):
    model = Termin
    form_class = TerminForm
    template_name = 'price/termin_form.html'
    success_url = reverse_lazy('termin_list')

class TerminDeleteView(DeleteView):
    model = Termin
    template_name = 'price/termin_confirm_delete.html'
    success_url = reverse_lazy('termin_list')