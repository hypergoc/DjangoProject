# gemini/views.py

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import GeminiQuery


# Ovdje ćemo kasnije dodati naš servis za AI
# from . import services 

# @staff_member_required osigurava da samo ulogovani admini mogu pristupiti
@staff_member_required
def chat_interface_view(request):
    """
    Glavni view za naš chat interfejs.
    """
    # Ako korisnik pošalje formu (stisne gumb "Pošalji")
    if request.method == 'POST':
        # Uzimamo pitanje iz forme
        user_question = request.POST.get('question', '').strip()

        if user_question:
            # --- OVDJE ĆE IĆI AI LOGIKA ---
            # Za sada, samo ćemo kreirati lažni odgovor da testiramo
            ai_response = f"Ovo je privremeni odgovor na pitanje: '{user_question}'"

            # Spremamo i pitanje i odgovor u našu bazu podataka
            GeminiQuery.objects.create(
                question=user_question,
                response=ai_response
            )

            # Preusmjeravamo nazad na istu stranicu da se forma ne bi ponovno poslala
            return redirect('gemini:chat_interface')

    # Ako je običan GET zahtjev (samo učitavanje stranice),
    # dohvaćamo sve zapise iz baze da ih prikažemo.
    # Znak minus ispred 'timestamp' sortira od najnovijeg prema najstarijem.
    chat_history = GeminiQuery.objects.all().order_by('timestamp')

    context = {
        'title': 'Gemini Chat Interface',
        'chat_history': chat_history,
    }

    # Prikazujemo HTML templejt (koji ćemo sada kreirati)
    return render(request, 'gemini/chat_page.html', context)