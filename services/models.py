from django.db import models

class Service(models.Model):
    title = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Tvoji flagovi
    is_per_night = models.BooleanField(default=False)
    is_per_person = models.BooleanField(default=False)
    # Dodajemo: Da li se dodaje automatski na svaki novi booking?
    is_global_default = models.BooleanField(default=False, help_text="Automatski dodaj na svaki novi booking?")

    def __str__(self):
        return f"{self.title} ({self.default_price} EUR)"


class BookingService(models.Model):  # Preimenovao sam Service u BookingService radi jasnoće
    booking = models.ForeignKey('bookingengine.Booking', on_delete=models.CASCADE, related_name='services')
    # Denormaliziramo podatke (kopiramo) da ostanu fiksni za ovaj booking
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Cijena po jedinici
    quantity = models.PositiveIntegerField(default=1)

    # Kopiramo i logiku, jer se definicija može promijeniti
    is_per_night = models.BooleanField(default=False)

    # Link na original (opcionalno)
    definition = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL)

    def total_cost(self, nights):
        # Tvoja formula: price * quantity * (nights ako je per_night inače 1)
        multiplier = nights if self.is_per_night else 1

        # price engine calculator
        return self.price * self.quantity * multiplier