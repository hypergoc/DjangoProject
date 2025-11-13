# resizer.py
import os
from PIL import Image, UnidentifiedImageError

# --- KONFIGURACIJA ---
TARGET_WIDTH = 310
TARGET_HEIGHT = 414
TARGET_ASPECT = TARGET_WIDTH / TARGET_HEIGHT
INPUT_FOLDER = os.path.join('media', 'new')
OUTPUT_FOLDER = os.path.join('media', 'resized')


# --------------------

def resize_and_crop(image_path, output_path):
    """
    Sada radi bez ikakve konverzije color profila, čuvajući prozirnost.
    """
    try:
        img = Image.open(image_path)
        original_format = img.format

        # OBRISALI SMO CIJELI BLOK ZA KONVERZIJU U RGB.
        # SADA RADIMO DIREKTNO S ORIGINALNOM SLIKOM, KAKVA GOD DA JE.

        source_width, source_height = img.size
        source_aspect = source_width / source_height

        if source_aspect > TARGET_ASPECT:
            # Slika je šira, režemo lijevo i desno
            new_width = int(TARGET_ASPECT * source_height)
            left = (source_width - new_width) / 2
            right = source_width - left
            crop_box = (left, 0, right, source_height)
        else:
            # Slika je viša, režemo gore i dolje
            new_height = int(source_width / TARGET_ASPECT)
            top = (source_height - new_height) / 2
            bottom = source_height - top
            crop_box = (0, top, source_width, bottom)

        cropped_img = img.crop(crop_box)
        resized_img = cropped_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

        # Pripremamo opcije za spremanje
        save_options = {}
        # if original_format.upper() in ['JPEG', 'JPG']:
        #     save_options['quality'] = 95
        # elif original_format.upper() == 'PNG':
        #     save_options['optimize'] = True

        # Spremanje s originalnim formatom
        resized_img.save(output_path, format=original_format, **save_options)

        print(f"USPJEH: Slika '{os.path.basename(image_path)}' je obrađena.")

    except UnidentifiedImageError:
        print(f"GREŠKA: Fajl '{os.path.basename(image_path)}' nije prepoznat kao slika.")
    except Exception as e:
        print(f"GREŠKA: Nije moguće obraditi '{os.path.basename(image_path)}'. Razlog: {e}")


def main():
    """ Glavna funkcija koja pokreće cijeli proces. """
    print("--- Pokrećem The TineLine Resizer v2.2 ---")

    if not os.path.exists(INPUT_FOLDER):
        print(f"GREŠKA: Ulazni folder '{INPUT_FOLDER}' ne postoji.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        print(f"Kreiram izlazni folder: '{OUTPUT_FOLDER}'")
        os.makedirs(OUTPUT_FOLDER)

    # Lista već obrađenih slika da izbjegnemo dupli rad
    processed_files = set(os.listdir(OUTPUT_FOLDER))

    for filename in sorted(os.listdir(INPUT_FOLDER)):
        if filename in processed_files:
            # print(f"INFO: Slika '{filename}' je već obrađena, preskačem.")
            continue

        if filename.lower().endswith(('.png', '.jpg', 'jpeg', '.webp')):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            resize_and_crop(input_path, output_path)

    print("--- Proces završen. ---")


if __name__ == '__main__':
    main()