from django import forms
from .models import Apartman

class ApartmanForm(forms.ModelForm):
    class Meta:
        model = Apartman
        fields = ['naziv', 'company', 'size', 'opis', 'additional_content']