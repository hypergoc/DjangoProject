from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Company
from .forms import CompanyForm

class CompanyListView(ListView):
    model = Company
    template_name = 'company/company_list.html'
    context_object_name = 'companies'

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company/company_detail.html'

class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/company_form.html'
    success_url = reverse_lazy('company_list')

class CompanyUpdateView(UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/company_form.html'
    success_url = reverse_lazy('company_list')

class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'company/company_confirm_delete.html'
    success_url = reverse_lazy('company_list')