from django.db import models

class Setting(models.Model):
    path = models.CharField(
        "Putanja (ključ)",
        max_length=255,
        unique=True,
        help_text="Jedinstvena putanja do postavke, npr. 'general.site_name'"
    )
    value = models.CharField(
        "Vrijednost",
        max_length=2000,
        blank=True,
        help_text="Vrijednost postavke."
    )
    default = models.BooleanField(
        "Zadana postavka",
        default=False,
        help_text="Označava je li ovo sistemska, zadana postavka."
    )

    def __str__(self):
        return self.path

    class Meta:
        verbose_name = "Postavka"
        verbose_name_plural = "Postavke"