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
    discount_percent = models.DecimalField(verbose_name="Discount percent", decimal_places=2, max_digits=10, blank=True, null=True)
    discount_amount = models.DecimalField(verbose_name="Discount amount", decimal_places=2, max_digits=10, blank=True, null=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Ukupna cijena bookinga")
    additional_requests = models.TextField(blank=True, null=True, verbose_name="Dodatni zahtjevi (Napomene)")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Popust %")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Popust Iznos (EUR)")

    # Spajamo Managera
    objects = BookingManager()

    def clean(self):
        # Validacija prije save-a. Ovdje provjeravamo je li period slobodan.
        # (Osim ako je ovo postojeći booking koji nije mijenjao datume, ali to je detalj)
        super().clean()
        # Ovdje možeš dodati: if not Booking.objects.is_period_available(...)

    def save(self, *args, **kwargs):
        # 1. AUTO-POPUST OD KLIJENTA (Samo kod kreiranja)
        if not self.pk and self.customer:
            # Provjeravamo ima li customer polje 'discount_percent' i je li > 0
            if hasattr(self.customer, 'discount_percent') and self.customer.discount_percent > 0:
                self.discount_percent = self.customer.discount_percent

        # 2. IZRAČUN BRUTO CIJENE (Najam + Usluge)
        # Zovemo Managera da nam da "punu cijenu" prije popusta.
        # Pazi: save=False jer ćemo spremiti na kraju metode.
        # Moramo imati datume da bi ovo radilo.
        if self.date_from and self.date_to:
            try:
                gross_price = Booking.objects.calculate_total_price(self, save=False)
                self.price = gross_price
            except ValidationError as e:
                # Ako fali cijena u terminima, propuštamo grešku da je Admin uhvati
                raise e

        # 3. PRIMJENA POPUSTA
        # Logika: Percent ima prednost. Ako nema percent, gledamo fiksni iznos.
        if self.discount_percent > 0:
            discount_value = (self.price * self.discount_percent) / 100
            self.discount_amount = discount_value  # Zapišemo iznos popusta
            self.price -= discount_value  # Umanjimo ukupnu cijenu

        elif self.discount_amount > 0:
            # Ako je unesen samo fiksni iznos popusta
            self.price -= self.discount_amount

        # Osigurač da cijena ne ode u minus
        if self.price < 0:
            self.price = 0

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