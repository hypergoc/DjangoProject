from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from apartman.models import Apartman
from customer.models import Customer
from price.models import Termin


class Booking(models.Model):
    apartman = models.ForeignKey(Apartman, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    date_from = models.DateField(verbose_name="From date")
    date_to = models.DateField(verbose_name="To date")
    visitors_count = models.PositiveIntegerField(default=1)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(default=0,  max_digits=10, decimal_places=2, verbose_name="Ukupna cijena bookinga")

    def save(self, *args, **kwargs):
        if self.date_from and self.date_to and self.price == 0:
            total_price = 0
            current_date = self.date_from
            while current_date < self.date_to:
                # Za SVAKI dan u booking-u, pronalazimo odgovarajući Termin (i cijenu)
                termin_za_dan = Termin.objects.filter(
                    apartman=self.apartman,
                    date_from__lte=current_date,
                    date_to__gt=current_date  # Koristimo __gt umjesto __gte za kraj, jer noćenje završava ujutro
                ).first()

                if termin_za_dan:
                    total_price += termin_za_dan.value
                else:
                    # Ako za neki dan ne postoji cijena, digni grešku!
                    raise ValidationError(
                        f"Cijena za datum {current_date} nije definirana. Booking se ne može stvoriti.")

                current_date += timedelta(days=1)

            # Postavljamo izračunatu cijenu na objekt koji se sprema
            self.price = total_price

        # Na kraju, POZIVAMO ORIGINALNU save metodu da odradi spremanje u bazu.
        # Ovo je KRITIČNO VAŽNO.
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
        # verbose_name je ime koje će se prikazati u admin panelu.
        verbose_name = 'Search'
        verbose_name_plural = 'Search'