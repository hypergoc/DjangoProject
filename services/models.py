from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Service(models.Model):
    """Katalog Usluga (Šifarnik)"""
    title = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_per_night = models.BooleanField(default=False)
    is_per_person = models.BooleanField(default=False)
    is_global_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.default_price}€)"

class ServicePrice(models.Model):
    """Sezonski Cjenik"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='seasonal_prices', null=True)
    date_from = models.DateField()
    date_to = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class BookingService(models.Model):
    """
    Čista vezna tablica (Link).
    Samo kaže: Ovaj Booking ima Ovu Uslugu (toliko komada).
    """
    booking = models.ForeignKey('bookingengine.Booking', on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Usluga") # Preimenovao sam definition u service jer je logičnije
    quantity = models.PositiveIntegerField(default=1, verbose_name="Količina")

    def __str__(self):
        return f"{self.service.title} x {self.quantity}"

    # Nema više name, price, is_per_night. Sve čitamo iz self.service!

# --- SIGNAL ZA REKALKULACIJU ---
@receiver(post_save, sender=BookingService)
@receiver(post_delete, sender=BookingService)
def update_booking_total(sender, instance, **kwargs):
    if instance.booking:
        from bookingengine.models import Booking
        Booking.objects.calculate_total_price(instance.booking, save=True)