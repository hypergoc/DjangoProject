# gemini/services.py

import os
from dotenv import load_dotenv
import google.generativeai as genai
from .models import GeminiQuery

# Učitava varijable iz .env fajla
load_dotenv()

# Konfiguracija API ključa
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    raise Exception("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")


def get_ai_response(prompt: str):
    """
    Vraća tuple: (tekst_odgovora, sirovi_response, tokeni, poslani_request)
    """
    try:
        # --- TVOJA GENIJALNA LINIJA KODA ---
        # Učitavamo ime modela iz .env fajla
        model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")  # "gemini-pro" je fallback
        model = genai.GenerativeModel(model_name=model_name)
        # ------------------------------------

        # Učitavamo povijest iz baze (zadnjih 10 zapisa)
        history_from_db = GeminiQuery.objects.all().order_by('-timestamp')[:10]

        # Formatiramo povijest za API
        api_history = []
        for entry in reversed(history_from_db):
            api_history.append({"role": "user", "parts": [entry.question]})
            api_history.append({"role": "model", "parts": [entry.response]})

        # Ovo je naš 'client_request' paket koji ćemo spremiti
        full_request_payload = {
            "model_used": model_name,
            "history": api_history,
            "prompt": prompt
        }

        # Započinjemo chat s postojećom povijesti
        chat = model.start_chat(history=api_history)
        response = chat.send_message(prompt)

        ai_response_text = response.text

        try:
            from google.protobuf.json_format import MessageToDict
            raw_response_dict = MessageToDict(response._result)
        except Exception:
            raw_response_dict = {'error': 'Could not serialize response object', 'text': ai_response_text}

        total_tokens = response.usage_metadata.total_token_count

        # Vraćamo sve, uključujući i request paket
        return ai_response_text, raw_response_dict, total_tokens, full_request_payload

    except Exception as e:
        print(f"Greška prilikom poziva Gemini API-ja: {e}")
        error_text = f"Došlo je do greške u komunikaciji s Gemini API-jem: {str(e)}"
        # Kreiramo payload čak i u slučaju greške
        error_payload = {
            "model_used": os.environ.get("GEMINI_MODEL", "gemini-pro"),
            "history": "N/A",
            "prompt": prompt,
            "error": str(e)
        }
        # Vraćamo ispravan broj vrijednosti
        return error_text, {'error': str(e)}, None, error_payload