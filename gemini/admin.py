# gemini/admin.py

from django.contrib import admin
from .models import GeminiQuery
from . import services


@admin.register(GeminiQuery)
class GeminiQueryAdmin(admin.ModelAdmin):
    # Podešavanja za prikaz liste
    list_display = ('question', 'response', 'token_count', 'timestamp')
    ordering = ('-timestamp',)

    # Polja samo za čitanje u detaljnom prikazu
    readonly_fields = ('timestamp', 'raw_response', 'client_request')

    # Hakirana funkcija koja sada radi sve što treba
    def changelist_view(self, request, extra_context=None):
        if '_run_ai_query' in request.POST:
            question = request.POST.get('ai_question')
            if question:

                # Primamo 4 vrijednosti iz servisa
                ai_response, raw_resp_dict, tokens, request_payload = services.get_ai_response(question)

                # Spremamo sve u bazu
                GeminiQuery.objects.create(
                    question=question,
                    response=ai_response,
                    raw_response=raw_resp_dict,
                    token_count=tokens,
                    client_request=request_payload
                )

                # Prikazujemo poruku o uspjehu
                message = f"AI Query uspješno izvršen."
                if tokens is not None:
                    message += f" Potrošeno tokena: {tokens}"
                self.message_user(request, message)

        return super().changelist_view(request, extra_context=extra_context)