from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'company',
            'name',
            'surname',
            'email',
            'phone',
            'address',
            'city',
            'country',
            'vat',
            'additional_data',
        ]