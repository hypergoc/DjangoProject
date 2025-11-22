from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


# Pazi: Koristimo lazy import ('bookingengine.Booking') da izbjegnemo kružne reference

class Service(models.Model):
    """
    Globalni Katalog Usluga (Šifarnik).
    Ovdje definiraš što nudiš i koja je default cijena.
    """
    title = models.CharField(max_length=255, verbose_name="Naziv usluge")
    default_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Default Cijena")

    # Logika naplate
    is_per_night = models.BooleanField(default=False, verbose_name="Po noćenju?")
    is_per_person = models.BooleanField(default=False, verbose_name="Po osobi/komadu?")

    # Automatika
    is_global_default = models.BooleanField(
        default=False,
        verbose_name="Globalni Default",
        help_text="Automatski dodaj na svaki novi booking?"
    )

    def __str__(self):
        mode = []
        if self.is_per_night: mode.append("Noćenja")
        if self.is_per_person: mode.append("Kom")
        logic = " * ".join(mode) if mode else "Fiksno"
        return f"{self.title} ({self.default_price} EUR) [{logic}]"

    class Meta:
        verbose_name = "Katalog Usluga"
        verbose_name_plural = "Katalog Usluga"


class ServicePrice(models.Model):
    """
    Sezonski cjenik za usluge iz kataloga.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='seasonal_prices',
        verbose_name="Usluga"
    )
    date_from = models.DateField(verbose_name="Od datuma")
    date_to = models.DateField(verbose_name="Do datuma")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sezonska Cijena"
    )

    def __str__(self):
        return f"{self.service.title}: {self.price} EUR ({self.date_from} - {self.date_to})"

    class Meta:
        verbose_name = "Sezonska Cijena Usluge"
        verbose_name_plural = "Cjenik Usluga (Sezonski)"
        ordering = ['service', 'date_from']


class BookingService(models.Model):
    """
    Stvarna usluga dodana na Booking. Redak na računu.
    """
    booking = models.ForeignKey(
        'bookingengine.Booking',  # Lazy import
        on_delete=models.CASCADE,
        related_name='services'
    )

    # Link na katalog (opcionalno, radi searcha)
    definition = models.ForeignKey(
        Service,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Iz Kataloga"
    )

    # Denormalizirani podaci (kopirani, da ostanu fiksni)
    name = models.CharField(max_length=255, verbose_name="Naziv stavke", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cijena", blank=True, null=True)

    quantity = models.PositiveIntegerField(default=1, verbose_name="Količina")

    # Logika (također kopirana)
    is_per_night = models.BooleanField(default=False, verbose_name="Po noći?")

    def __str__(self):
        return f"{self.name} x {self.quantity}"

    class Meta:
        verbose_name = "Dodatna Usluga"
        verbose_name_plural = "Dodatne Usluge"


# --- SIGNALI ---

@receiver(pre_save, sender=BookingService)
def fill_service_details(sender, instance, **kwargs):
    """
    Prije spremanja, ako je korisnik odabrao 'definition' a nije upisao ime/cijenu,
    kopiraj ih iz kataloga.
    """
    if instance.definition:
        # 1. Ime
        if not instance.name:
            instance.name = instance.definition.title

        # 2. Logika
        # Ako je novi objekt (nema PK), kopiraj logiku
        if not instance.pk:
            instance.is_per_night = instance.definition.is_per_night

        # 3. Cijena
        if not instance.price:
            # Provjeri sezonsku cijenu! (Malo naprednije, ali korisno)
            # Budući da ne znamo točne datume bookinga ovdje lako (treba upit),
            # uzimamo default. Sezonska cijena će se ionako računati u Manageru bookinga.
            instance.price = instance.definition.default_price


@receiver(post_save, sender=BookingService)
@receiver(post_delete, sender=BookingService)
def update_booking_total(sender, instance, **kwargs):
    """
    Kad se doda/promijeni/obriše servis, ponovno izračunaj cijenu Bookinga.
    """
    if instance.booking:
        # Lazy import Managera/Modela da izbjegnemo kružni pakao
        from bookingengine.models import Booking

        # Pozivamo metodu iz Managera koja sve zbraja
        # Pazi: ovo okida save() na bookingu
        try:
            Booking.objects.calculate_total_price(instance.booking, save=True)
        except Exception as e:
            # Logiraj grešku, nemoj srušiti admina
            print(f"Greška pri rekalkulaciji bookinga {instance.booking.id}: {e}")