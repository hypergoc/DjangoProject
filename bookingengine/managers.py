from django.db import models
from django.core.exceptions import ValidationError
from price.models import Termin
from apartman.models import Apartman
from datetime import timedelta

class BookingManager(models.Manager):
    def calculate_price_for_period(self, apartman, date_from, date_to):
        """
        OVO JE MOTOR. Naša sveta, reusable metoda.
        Prima apartman, početni i krajnji datum, vraća izračunatu cijenu ili diže grešku.
        """
        if not all([apartman, date_from, date_to]):
            return 0  # Vraća 0 ako podaci nisu kompletni

        total_price = 0
        current_date = date_from
        while current_date < date_to:
            termin_za_dan = Termin.objects.filter(
                apartman=apartman,
                date_from__lte=current_date,
                date_to__gt=current_date
            ).first()

            if termin_za_dan:
                total_price += termin_za_dan.value
            else:
                raise ValidationError(f"Cijena za datum {current_date} nije definirana.")

            current_date += timedelta(days=1)

        return total_price

    def is_period_available(self, apartman, date_from, date_to):
        if not all([apartman, date_from, date_to]):
            return False

        overlapping_bookings = self.filter(
            apartman=apartman,
            date_from__lt=date_to,
            date_to__gt=date_from
        )

        is_overlapping = overlapping_bookings.exists()

        return not is_overlapping