from django.db import models
from django.core.exceptions import ValidationError
from apartman.models import Apartman
from customer.models import Customer
from .managers import BookingManager

class Booking(models.Model):
    apartman = models.ForeignKey(Apartman, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    date_from = models.DateField(verbose_name="From date")
    date_to = models.DateField(verbose_name="To date")
    visitors_count = models.PositiveIntegerField(default=1)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Ukupna cijena bookinga")

    # Spajamo Managera
    objects = BookingManager()

    def clean(self):
        # Validacija prije save-a. Ovdje provjeravamo je li period slobodan.
        # (Osim ako je ovo postojeći booking koji nije mijenjao datume, ali to je detalj)
        super().clean()
        # Ovdje možeš dodati: if not Booking.objects.is_period_available(...)

    def save(self, *args, **kwargs):
        # UVIJEK pokušaj izračunati cijenu prije spremanja.
        # Manager će se pobrinuti za logiku.
        if self.date_from and self.date_to:
            try:
                # Pozivamo našu centralnu logiku iz managera
                # save=False jer ćemo spremiti odmah u liniji ispod (super().save)
                calculated_price = Booking.objects.calculate_total_price(self, save=False)
                self.price = calculated_price
            except ValidationError as e:
                # Propustamo grešku dalje. Admin će je prikazati na vrhu forme.
                raise e

        # Na kraju, POZIVAMO ORIGINALNU save metodu da odradi spremanje u bazu.
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.apartman.naziv} by {self.customer} from {self.date_from} to {self.date_to}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-date_from']


class BookingSearch(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Search'
        verbose_name_plural = 'Search'