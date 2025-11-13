from django.db import models
# Assuming the app from the previous request is named 'company'
from company.models import Company

class Apartman(models.Model):
    naziv = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='apartmani')
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in square meters (m²)")
    opis = models.TextField(blank=True, null=True)
    additional_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.naziv