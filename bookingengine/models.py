from django.db import models
from apartman.models import Apartman
# Assuming a 'customer' app with a 'Customer' model exists.
# If not, you would need to create it.
# Example: from django.contrib.auth.models import User as Customer
from customer.models import Customer


class Booking(models.Model):
    apartman = models.ForeignKey(Apartman, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    date_from = models.DateField(verbose_name="From date")
    date_to = models.DateField(verbose_name="To date")
    visitors_count = models.PositiveIntegerField(default=1)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.apartman.naziv} by {self.customer} from {self.date_from} to {self.date_to}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-date_from']