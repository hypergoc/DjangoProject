from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    vat = models.CharField(max_length=50, blank=True, null=True, verbose_name="VAT number")
    additional_data = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.surname}" if self.surname else self.name