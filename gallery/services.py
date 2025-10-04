import cv2
import numpy as np
from gallery.models import Image as ImagesModel


# def get_stored_images(count=100):
    # images_collection = ImagesModel.objects.filter(used=0, is_disabled=0).
    # stored_images = []
    # for i in range(count):

def izracunaj_histogram_ruba(rub):
    """
    Prima dio slike (rub) i vraća normalizirani 3D histogram boja.
    """
    # Smanjimo broj "kanti" (bins) za bržu i često robusniju usporedbu
    hist = cv2.calcHist([rub], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist.flatten()


# --- GLAVNI DIO ---

# Učitaj dvije slike koje želiš usporediti
try:
    slika_A = cv2.imread('slika_A.jpg')
    slika_B = cv2.imread('slika_B.jpg')

    if slika_A is None or slika_B is None:
        raise FileNotFoundError("Jedna od slika nije pronađena.")

    # 1. Izoliraj relevantne rubove
    sirina_A = slika_A.shape[1]
    desni_rub_A = slika_A[:, int(sirina_A * 0.9):]  # Zadnjih 10% širine

    sirina_B = slika_B.shape[1]
    lijevi_rub_B = slika_B[:, 0:int(sirina_B * 0.1)]  # Prvih 10% širine

    # 2. Izračunaj "potpise" (histograme) za oba ruba
    hist_A = izracunaj_histogram_ruba(desni_rub_A)
    hist_B = izracunaj_histogram_ruba(lijevi_rub_B)

    # 3. Usporedi histograme i izračunaj sličnost
    # OpenCV-u treba float32 tip za usporedbu
    hist_A = np.float32(hist_A)
    hist_B = np.float32(hist_B)

    metode = {
        "Correlation": cv2.HISTCMP_CORREL,
        "Chi-Squared": cv2.HISTCMP_CHISQR,
        "Intersection": cv2.HISTCMP_INTERSECT,
        "Bhattacharyya": cv2.HISTCMP_BHATTACHARYYA
    }

    print(f"Usporedba prijelaza 'slika_A.jpg' -> 'slika_B.jpg':\n")
    for naziv, metoda in metode.items():
        slicnost = cv2.compareHist(hist_A, hist_B, metoda)
        print(f"{naziv}: {slicnost:.4f}")
        if naziv == "Correlation":
            print("  (Više je bolje, idealno 1.0)")
        elif naziv == "Chi-Squared":
            print("  (Niže je bolje, idealno 0.0)")
        elif naziv == "Intersection":
            print("  (Više je bolje)")
        elif naziv == "Bhattacharyya":
            print("  (Niže je bolje, idealno 0.0)")
        print("-" * 30)

except FileNotFoundError as e:
    print(e)
    print("Molim te stavi 'slika_A.jpg' i 'slika_B.jpg' u isti folder.")