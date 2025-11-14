from django import forms
from .models import Termin

class TerminForm(forms.ModelForm):
    class Meta:
        model = Termin
        fields = ['apartman', 'date_from', 'date_to', 'value']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }