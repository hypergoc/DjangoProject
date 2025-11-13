from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Apartman
from .forms import ApartmanForm

class ApartmanListView(ListView):
    model = Apartman
    template_name = 'apartman/apartman_list.html'
    context_object_name = 'apartmani'

class ApartmanDetailView(DetailView):
    model = Apartman
    template_name = 'apartman/apartman_detail.html'
    context_object_name = 'apartman'

class ApartmanCreateView(CreateView):
    model = Apartman
    form_class = ApartmanForm
    template_name = 'apartman/apartman_form.html'
    success_url = reverse_lazy('apartman_list')

class ApartmanUpdateView(UpdateView):
    model = Apartman
    form_class = ApartmanForm
    template_name = 'apartman/apartman_form.html'
    success_url = reverse_lazy('apartman_list')

class ApartmanDeleteView(DeleteView):
    model = Apartman
    template_name = 'apartman/apartman_confirm_delete.html'
    success_url = reverse_lazy('apartman_list')