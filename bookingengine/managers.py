from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q  # Trebat će nam za pretragu sezonskih cijena
from datetime import timedelta
from decimal import Decimal

# Importamo modele koje trebamo. Pazi na putanje!
from price.models import Termin


# from services.models import ServicePrice, BookingService -> Ovo ćemo dohvaćati dinamički ili preko relacija

class BookingManager(models.Manager):

    def calculate_total_price(self, booking_instance, save=False):
        """
        Glavna metoda. Prima instancu Bookinga (koja ima datume, apartman, ljude i SERVISE).
        Vraća ukupnu cijenu.
        Ako save=True, odmah sprema cijenu u objekt.
        """
        if not booking_instance.apartman or not booking_instance.date_from or not booking_instance.date_to:
            return Decimal('0.00')

        # 1. OSNOVNA CIJENA (NAJAM APARTMANA)
        base_price = self._calculate_base_stay_price(
            booking_instance.apartman,
            booking_instance.date_from,
            booking_instance.date_to
        )

        # 2. CIJENA USLUGA (EXTRA SERVICES)
        # Ovo pretpostavlja da su BookingService objekti VEĆ kreirani i vezani za booking.
        # (To smo riješili u Adminu onim save_model hookom ili inline-om)
        services_price = self._calculate_services_price(booking_instance)

        total = base_price + services_price

        if save:
            booking_instance.price = total
            booking_instance.save(update_fields=['price'])  # Čuvamo samo cijenu

        return total

    def _calculate_base_stay_price(self, apartman, date_from, date_to):
        """
        Interna metoda: Računa samo cijenu noćenja iz Termina.
        """
        total = Decimal('0.00')
        current_date = date_from

        while current_date < date_to:
            termin = Termin.objects.filter(
                apartman=apartman,
                date_from__lte=current_date,
                date_to__gt=current_date
            ).order_by('-id').first()

            if termin:
                # Pretpostavljam da je termin.value float, pretvaramo u Decimal
                total += Decimal(str(termin.value))
            else:
                raise ValidationError(f"Cijena za datum {current_date} nije definirana u Terminima.")

            current_date += timedelta(days=1)

        return total

    def _calculate_services_price(self, booking):
        """
        Interna metoda: Računa cijenu svih dodatnih usluga na bookingu.
        """
        total_services = Decimal('0.00')
        nights = (booking.date_to - booking.date_from).days
        if nights < 1: nights = 1

        # Prolazimo kroz sve servise vezane uz ovaj booking
        # booking.services je related_name iz modela BookingService
        for booking_service in booking.services.all():

            # A. Određivanje jedinične cijene (Base Unit Price)
            # Moramo vidjeti ima li SEZONSKA cijena za ovaj period?
            # Ovo je malo tricky jer servis može trajati više dana.
            # Radi jednostavnosti (KISS), uzimamo cijenu na PRVI DAN bookinga
            # ili (naprednije) radimo prosjek.
            # OVDJE KORISTIM JEDNOSTAVNIJU LOGIKU:
            # Ako postoji ServicePrice koji pokriva START DATE bookinga, uzmi tu cijenu.
            # Inače uzmi booking_service.price (koja je kopirana s definicije).

            unit_price = booking_service.price  # Default (kopirana cijena)

            if booking_service.definition:
                # Provjera sezonske cijene u katalogu
                seasonal = booking_service.definition.seasonal_prices.filter(
                    date_from__lte=booking.date_from,
                    date_to__gte=booking.date_from
                ).first()

                if seasonal:
                    unit_price = seasonal.price

            # B. Izračun Faktora (Multipliers)
            qty_factor = booking_service.quantity  # Npr. 2 osobe, 3 psa

            time_factor = 1
            if booking_service.is_per_night:
                time_factor = nights

            # C. Finalni izračun za ovu stavku
            line_total = unit_price * qty_factor * time_factor

            total_services += line_total

        return total_services

    # ... tvoj is_period_available ostaje isti ...
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