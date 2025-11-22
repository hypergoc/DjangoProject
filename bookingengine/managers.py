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
        total = Decimal('0.00')
        nights = (booking.date_to - booking.date_from).days
        if nights < 1: nights = 1

        for bs in booking.services.all():
            # Dohvaćamo definiciju direktno
            definition = bs.service

            # 1. Nađi cijenu (Sezonska ili Default)
            unit_price = definition.default_price

            seasonal = definition.seasonal_prices.filter(
                date_from__lte=booking.date_from,
                date_to__gte=booking.date_from
            ).first()

            if seasonal:
                unit_price = seasonal.price

            # 2. Množitelji (čitamo ih iz definicije!)
            qty_factor = bs.quantity

            time_factor = 1
            if definition.is_per_night:  # Čitamo iz definicije
                time_factor = nights

            if definition.is_per_person:  # Ako imaš i ovo
                # Ovdje pazi: bs.quantity je količina USLUGE.
                # Ako je usluga npr. "Doručak" i quantity je 2 (za 2 osobe), to je to.
                pass

            total += unit_price * qty_factor * time_factor

        return total

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