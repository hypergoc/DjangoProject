# imagen/services.py

import os
from datetime import datetime
import google.generativeai as genai
from google.genai import types
from google.genai import Client  # <<< Tvoj ispravan import
from django.core.files.base import ContentFile
from .models import ContentGeneration, Path, GeneratedImage
from dotenv import load_dotenv
import logging
import json
from settings.models import Setting as SettingsModel

load_dotenv()
logger = logging.getLogger(__name__)

# API ključ se čita nakon što je .env učitan
apiKey = os.environ.get("GOOGLE_API_KEY")
if not apiKey:
    raise ValueError("GOOGLE_API_KEY nije postavljen u .env fajlu.")


# --------------------------------

# Tvoja originalna get_gemini_text_response funkcija ostaje ista
def get_gemini_text_response(prompt: str):
    """
    Generira tekstualni odgovor koristeći Gemini.
    """
    logger.info("Pokrećem 'get_gemini_text_response'...")

    genai.configure(api_key=apiKey)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")

    additional_prompt = SettingsModel.objects.filter(path="imagen/contentgeneration/gemini_rule").first().value
    if additional_prompt:
        prompt = f"{prompt} ({additional_prompt})"

    model = genai.GenerativeModel(model_name=model_name)
    response = model.generate_content(prompt)


# Tvoja generate_imagen_image funkcija, sada s ispravnim loggerom
def generate_imagen_image(content_gen: ContentGeneration):
    logger.info(f'Pokrećem generate_imagen_image za objekt ID: {content_gen.pk}')

    if not content_gen.prompt:
        logger.error("Prompt je prazan. Prekidam.")
        raise ValueError("Prompt je prazan. Ne mogu generirati sliku.")


    # Tvoj ispravan kod za Imagen
    genai.configure(api_key=apiKey)
    model_name = os.getenv("IMAGEN_MODEL_NAME")
    client = Client(api_key=apiKey)

    logger.debug(serialize_for_logging(client))
    logger.debug(model_name)
    logger.debug(content_gen.prompt)
    logger.debug(apiKey)

    response = client.models.generate_images(
        model=model_name,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            include_rai_reason=True,
            aspect_ratio="1:1",
            # aspect_ratio="3:4",
            # aspect_ratio="9:16",
        ),
        prompt=content_gen.prompt
    )

    if not response.generated_images:
        logger.debug(
            f"CIJELI SIROVI ODGOVOR (pretvoren u tekst):\n{serialize_for_logging(response)}"
        )
        raise Exception("Image generation failed. API did not return any images. Bla Bla poruka")

    # Osiguraj da postoji Path objekt na koji se vežu slike
    if not content_gen.path:
        path_obj = Path.objects.create(final_prompt=content_gen.prompt)
        content_gen.path = path_obj
        content_gen.save()

    # Spremanje generirane slike
    image_object = response.generated_images[0]
    image_bytes = image_object.image.image_bytes
    content_file = ContentFile(image_bytes)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ig_{timestamp}.png"

    new_image = GeneratedImage(path=content_gen.path)
    new_image.image_file.save(filename, content_file, save=True)

    # Ažuriranje brojača
    content_gen.image_count = content_gen.path.images.count()
    content_gen.save(update_fields=['image_count'])

    return new_image



# Helper funkcija za sigurno logiranje bilo kojeg objekta
def serialize_for_logging(data_object):
    """
    Univerzalni helper za pretvaranje bilo kojeg objekta u string za logiranje.
    """
    if isinstance(data_object, dict):
        return json.dumps(data_object, indent=4, ensure_ascii=False)
    if hasattr(data_object, '__dict__'):
        try:
            return json.dumps(vars(data_object), indent=4, ensure_ascii=False, default=str)
        except TypeError:
            pass
    return str(data_object)