from django.db import models
from apartman.models import Apartman
from services.models import Service

class Termin(models.Model):
    apartman = models.ForeignKey(Apartman, on_delete=models.CASCADE, related_name='termini')
    date_from = models.DateField(verbose_name="From")
    date_to = models.DateField(verbose_name="To")
    value = models.FloatField(default=0.0, verbose_name="Price")

    def __str__(self):
        return f"{self.apartman.naziv} ({self.date_from.strftime('%d.%m.%Y')} - {self.date_to.strftime('%d.%m.%Y')}) - {self.value}"

    class Meta:
        verbose_name = "Cijena"
        verbose_name_plural = "Cijene"
        ordering = ['date_from']
