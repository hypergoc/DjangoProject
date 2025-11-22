from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import timedelta
from decimal import Decimal

# Importamo modele koji su sigurni (nemaju kružnu ovisnost prema Bookingu)
from price.models import Termin
from apartman.models import Apartman


class BookingManager(models.Manager):

    def calculate_total_price(self, booking_instance, save=False):
        """
        Glavna metoda. Prima instancu Bookinga.
        Računa: Osnovna cijena (iz Termina) + Dodatne usluge (iz BookingService).

        Args:
            booking_instance: Objekt Bookinga (mora imati apartman, datume).
            save (bool): Ako je True, odmah sprema izračunatu cijenu u bazu.

        Returns:
            Decimal: Ukupna cijena.
        """
        # Osnovna provjera integriteta podataka
        if not booking_instance.apartman or not booking_instance.date_from or not booking_instance.date_to:
            return Decimal('0.00')

        # 1. OSNOVNA CIJENA (NAJAM APARTMANA PO NOĆENJU)
        try:
            print('base price')
            base_price = self._calculate_base_stay_price(
                booking_instance.apartman,
                booking_instance.date_from,
                booking_instance.date_to
            )
        except ValidationError:
            # Ovisno o strategiji, ovdje možemo ili propustiti grešku dalje (da je uhvati UI)
            # ili vratiti 0. Ako ovo zoveš iz Signala, bolje je propustiti grešku.
            raise

        # 2. CIJENA USLUGA (EXTRA SERVICES)
        # Oslanja se na to da su BookingService objekti već kreirani.
        services_price = self._calculate_services_price(booking_instance)

        # 3. ZBROJ
        total = base_price + services_price

        # Opcionalno spremanje
        if save:
            booking_instance.price = total
            # Koristimo update_fields radi brzine i sigurnosti (da ne pregazimo druge promjene)
            booking_instance.save(update_fields=['price'])

        return total

    def _calculate_base_stay_price(self, apartman, date_from, date_to):
        """
        Interna metoda: Računa sumu cijena noćenja iz modela Termin.
        """
        total = Decimal('0.00')
        current_date = date_from

        # Petlja kroz svaki dan boravka (osim zadnjeg dana odjave)
        while current_date < date_to:
            # Tražimo cijenu za taj specifičan datum
            # Logika: Najnoviji unesen termin (najveći ID) ima prednost
            termin = Termin.objects.filter(
                apartman=apartman,
                date_from__lte=current_date,
                date_to__gt=current_date
            ).order_by('-id').first()

            if termin:
                print(termin.pk)
                # Pretvaramo float/decimal u Decimal za precizno računanje novca
                total += Decimal(str(termin.value))
            else:
                # Ako fali cijena za ijedan dan, ovo je kritična greška
                raise ValidationError(f"Cijena za datum {current_date} nije definirana u Terminima.")

            current_date += timedelta(days=1)

        return total

    def _calculate_services_price(self, booking):
        """
        Interna metoda: Računa cijenu svih dodatnih usluga (BookingService) vezanih uz booking.
        Uključuje logiku za sezonske cijene usluga i množitelje (količina, noćenja).
        """
        total_services = Decimal('0.00')

        # Izračun broja noćenja
        nights = (booking.date_to - booking.date_from).days
        if nights < 1: nights = 1

        # Prolazimo kroz sve servise vezane uz ovaj booking
        # 'services' je related_name definiran u modelu BookingService
        for booking_service in booking.services.all():

            # A. ODREĐIVANJE JEDINIČNE CIJENE (Base Unit Price)
            # Početna pretpostavka: Cijena je ona koja piše na stavci
            unit_price = booking_service.price

            # Provjera sezonskih cijena (ako je servis vezan za definiciju u katalogu)
            if booking_service.definition:
                # Tražimo postoji li specifična cijena za period ovog bookinga
                # Pojednostavljenje: Gledamo cijenu na PRVI DAN bookinga
                seasonal = booking_service.definition.seasonal_prices.filter(
                    date_from__lte=booking.date_from,
                    date_to__gte=booking.date_from
                ).first()

                if seasonal:
                    unit_price = seasonal.price

            # B. IZRAČUN FAKTORA (Multipliers)
            # 1. Količina (npr. 3 osobe, 2 psa)
            qty_factor = booking_service.quantity

            # 2. Vrijeme (npr. 7 noćenja vs 1 fiksno čišćenje)
            time_factor = 1
            if booking_service.is_per_night:
                time_factor = nights

            # C. FINALNI IZRAČUN ZA OVU STAVKU
            line_total = unit_price * qty_factor * time_factor

            total_services += line_total

        return total_services

    def is_period_available(self, apartman, date_from, date_to):
        """
        Oracle metoda: Vraća True ako je apartman slobodan, False ako postoji preklapanje.
        """
        if not all([apartman, date_from, date_to]):
            return False

        # Tražimo bilo koji booking koji se preklapa s traženim periodom
        overlapping_bookings = self.filter(
            apartman=apartman,
            date_from__lt=date_to,  # Počinje prije nego što mi odlazimo
            date_to__gt=date_from  # Završava nakon što mi dolazimo
        )

        # .exists() je najbrži način provjere (vraća boolean)
        is_overlapping = overlapping_bookings.exists()

        # Ako postoji preklapanje, NIJE slobodno
        return not is_overlapping