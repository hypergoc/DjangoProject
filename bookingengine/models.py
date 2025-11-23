from django.db import models
from django.core.exceptions import ValidationError
from apartman.models import Apartman
from customer.models import Customer
from .managers import BookingManager
from django.contrib import messages

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
    additional_requests = models.TextField(blank=True, null=True, verbose_name="Dodatni zahtjevi (Napomene)")
    discount_percent = models.DecimalField(blank=True, default=0, null=True,max_digits=5, decimal_places=2, verbose_name="Popust %")
    discount_amount = models.DecimalField(blank=True, default=0, null=True, max_digits=10, decimal_places=2, verbose_name="Popust Iznos (EUR)")
    discount_percent_amount = models.DecimalField(blank=True, default=0, null=True, max_digits=10, decimal_places=2, verbose_name="Popust Iznos (EUR)")

    # Spajamo Managera
    objects = BookingManager()

    def clean(self):
        errors = {}

        if not self.apartman_id:  # Pazi: koristimo _id jer self.apartman može baciti grešku ako je None
            errors['apartman'] = "Molim odaberite apartman."

        if not self.customer_id:
            errors['customer'] = "Molim odaberite klijenta."

        if not self.date_from:
            errors['date_from'] = "Datum dolaska je obavezan."

        if not self.date_to:
            errors['date_to'] = "Datum odlaska je obavezan."

        if self.date_from and self.date_to:
            if self.date_from >= self.date_to:
                errors['date_to'] = "Datum odlaska mora biti nakon datuma dolaska."

        if self.visitors_count < 1:
            errors['visitors_count'] = "Broj gostiju mora biti barem 1."

        # Ako imamo osnovne greške, bacamo ih ODMAH.
        if errors:
            raise ValidationError(errors)
        # try:
        #     Booking.objects.calculate_total_price(self)  # Samo provjera
        # except ValidationError as e:
        #     raise ValidationError(f"Ne mogu spremiti: {e.message}")  # Ovo Admin lijepo prikaže
        # Validacija prije save-a. Ovdje provjeravamo je li period slobodan.
        # (Osim ako je ovo postojeći booking koji nije mijenjao datume, ali to je detalj)
        super().clean()
        # Ovdje možeš dodati: if not Booking.objects.is_period_available(...)

    def save(self, *args, **kwargs):

        if not self.pk:
            super().save(*args, **kwargs)

        # 1. AUTO-POPUST OD KLIJENTA (Samo kod kreiranja)
        if self.customer and (self.discount_percent is None or self.discount_percent == 0):
            customer_discount = getattr(self.customer, 'discount_percent', 0)
            if customer_discount > 0:
                self.discount_percent = customer_discount

        # 2. IZRAČUN BRUTO CIJENE (Najam + Usluge)
        # Uvijek računamo punu cijenu iz Managera
        if self.date_from and self.date_to:
            try:
                gross_price = Booking.objects.calculate_total_price(self, save=False)

                # Počinjemo od pune cijene
                final_price = gross_price

                # 3. PRIMJENA POPUSTA (STACKING / KUMULATIVNO)

                # A) Popust u postotku
                if self.discount_percent > 0:
                    percent_value = (gross_price * self.discount_percent) / 100
                    self.discount_percent_amount = percent_value
                    final_price -= percent_value

                # B) Popust u iznosu (Fiksni)
                # Sada ovo tretiramo kao DODATNI fiksni popust koji si ti upisao
                if self.discount_amount > 0:
                    final_price -= self.discount_amount



                # Osigurač (da ne moramo mi njima platiti)
                if final_price < 0:
                    final_price = 0

                self.price = final_price

            except ValidationError as e:
                raise e

        # 4. FINALNO SPREMANJE
        super(Booking, self).save(*args, **kwargs)

    @property
    def remaining_balance(self):
        total_paid = sum(p.amount for p in self.payments.all())
        return self.price - total_paid

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


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Iznos")
    payment_date = models.DateField(verbose_name="Datum uplate", auto_now_add=True)  # Ili ručno
    description = models.CharField(max_length=255, verbose_name="Opis", blank=True)

    # customer_id je redundantan jer ga imamo preko bookinga, ali ako baš želiš direktno, ok.
    # Ja preporučam povlačiti ga preko bookinga.

    def __str__(self):
        return f"{self.amount} EUR ({self.payment_date})"

    class Meta:
        verbose_name = "Uplata"
        verbose_name_plural = "Uplate"

class BookingCalendar(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Popunjenost (Kalendar)'
        verbose_name_plural = 'Popunjenost (Kalendar)'
