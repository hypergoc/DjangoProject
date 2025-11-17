from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['apartman', 'customer', 'date_from', 'date_to', 'visitors_count', 'approved']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }

class AvailabilityForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Datum dolaska")
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Datum odlaska")
    capacity = forms.IntegerField(min_value=1, label="Broj gostiju")