from django.db import models

class Customer(models.Model):
    company = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    vat = models.CharField(max_length=50, blank=True, null=True, verbose_name="VAT number")
    additional_data = models.TextField(blank=True, null=True)
    discount_percent = models.DecimalField(verbose_name="Discount percent", decimal_places=2, max_digits=10, blank=True, null=True)

    def __str__(self):
        if self.company:
            return f"{self.company} - {self.name} {self.surname}"
        return f"{self.name} {self.surname}"

    class Meta:
        ordering = ['company', 'surname', 'name']