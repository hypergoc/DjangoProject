import os
from datetime import datetime
import google.generativeai as genai
from google.genai import types
from google.genai import Client
from django.core.files.base import ContentFile
from .models import ContentGeneration, Path, GeneratedImage
from dotenv import load_dotenv
import logging
import json

load_dotenv()
logger = logging.getLogger(__name__)

apiKey = os.environ.get("GOOGLE_API_KEY")
if not apiKey:
    raise ValueError("GOOGLE_API_KEY nije postavljen u .env fajlu.")


def get_gemini_text_response(prompt: str, rules_geminy: str = ""):
    """
    Generira tekstualni odgovor koristeći Gemini, uzimajući u obzir dodatna pravila.
    """
    full_prompt = prompt
    if rules_geminy and rules_geminy.strip():
        # Spoji osnovni prompt s pravilima
        full_prompt = f"{full_prompt}\n\n--- Pravila ---\n{rules_geminy}"
    
    # Placeholder za vašu Gemini API logiku - zamijenite stvarnim pozivom
    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_NAME", "gemini-pro"))
    
    try:
        response = model.generate_content(full_prompt)
        ai_response_text = response.text
        # Neki modeli ne vraćaju usage_metadata, provjerite prije pristupa
        p_tokens = getattr(getattr(response, 'usage_metadata', None), 'prompt_token_count', 0)
        c_tokens = getattr(getattr(response, 'usage_metadata', None), 'completion_token_count', 0)
    except Exception as e:
        logger.error(f"Greška prilikom poziva Gemini API-ja: {e}")
        ai_response_text = f"Greška: {e}"
        p_tokens = 0
        c_tokens = 0

    return ai_response_text, p_tokens, c_tokens


def generate_imagen_image(content_gen: ContentGeneration):
    logger.info(f'Pokrećem generate_imagen_image za objekt ID: {content_gen.pk}')

    if not content_gen.prompt:
        logger.error("Prompt je prazan. Prekidam.")
        raise ValueError("Prompt je prazan. Ne mogu generirati sliku.")

    # Kombiniraj prompt i pravila za Imagen
    final_prompt_for_imagen = content_gen.prompt
    if content_gen.rules_imagen and content_gen.rules_imagen.strip():
        final_prompt_for_imagen = f"{content_gen.prompt}\n\n{content_gen.rules_imagen}"
        logger.info("Dodana su pravila za Imagen na prompt.")

    genai.configure(api_key=apiKey)
    model_name = os.getenv("IMAGEN_MODEL_NAME", "imagegeneration@005") # Default model
    client = Client(api_key=apiKey)

    logger.debug(f"Finalni prompt za Imagen: {final_prompt_for_imagen}")

    response = client.models.generate_images(
        model=model_name,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            include_rai_reason=True,
            aspect_ratio="1:1",
        ),
        prompt=final_prompt_for_imagen
    )

    if not response.generated_images:
        logger.debug(f"CIJELI SIROVI ODGOVOR: {serialize_for_logging(response)}")
        raise Exception("Generiranje slike nije uspjelo. API nije vratio slike.")

    if not content_gen.path:
        path_obj = Path.objects.create(final_prompt=final_prompt_for_imagen)
        content_gen.path = path_obj
        content_gen.save(update_fields=['path'])
    else:
        content_gen.path.final_prompt = final_prompt_for_imagen
        content_gen.path.save(update_fields=['final_prompt'])

    image_object = response.generated_images[0]
    image_bytes = image_object.image.image_bytes
    content_file = ContentFile(image_bytes)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ig_{timestamp}.png"

    new_image = GeneratedImage(path=content_gen.path)
    new_image.image_file.save(filename, content_file, save=True)

    content_gen.image_count = content_gen.path.images.count()
    content_gen.save(update_fields=['image_count'])

    return new_image


def serialize_for_logging(data_object):
    if isinstance(data_object, dict):
        return json.dumps(data_object, indent=4, ensure_ascii=False)
    if hasattr(data_object, '__dict__'):
        try:
            return json.dumps(vars(data_object), indent=4, ensure_ascii=False, default=str)
        except TypeError:
            pass
    return str(data_object)