# gemini/models.py

from django.db import models


class GeminiQuery(models.Model):
    question = models.TextField(verbose_name="Korisnikovo Pitanje")
    response = models.TextField(verbose_name="Geminijev Odgovor")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Vrijeme Zapisa")

    raw_response = models.JSONField(
        null=True, blank=True, verbose_name="Sirovi JSON Odgovor"
    )

    token_count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Broj Tokena"
    )

    client_request = models.JSONField(
        null=True, blank=True, verbose_name="Poslani API Request",
        help_text="JSON paket koji je poslan Gemini API-ju, uključujući povijest."
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Gemini Zapisi"

    def __str__(self):
        return f"Pitanje: '{self.question[:50]}...'"