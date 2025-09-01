# DjangoProject/logger_config.py

import logging

# --- OVO JE NAŠA CENTRALNA KONFIGURACIJA ZA LOGGING ---
logging.basicConfig(
    # 1. Ime fajla u koji će se sve zapisivati.
    #    Nalazit će se u rootu tvog projekta.
    filename='debug.log',

    # 2. Nivo logiranja. DEBUG je najniži, hvatat će SVE poruke.
    level=logging.DEBUG,

    # 3. Format svake linije u log fajlu.
    #    %(asctime)s - Vrijeme
    #    %(name)s - Ime modula (npr. gemini.services)
    #    %(levelname)s - Nivo (INFO, ERROR, etc.)
    #    %(message)s - Tvoja poruka
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    # 4. Format datuma i vremena
    datefmt='%Y-%m-%d %H:%M:%S',

    # 5. Način pisanja: 'w' = write (prepiši stari log svaki put).
    #    Za development je ovo najbolje da ti se log ne gomila.
    filemode='w'
)
# --------------------------------------------------------

# Samo informativna poruka da znamo da je ovaj fajl uspješno učitan
logging.info("--- Logger je uspješno konfiguriran i pokrenut iz logger_config.py. ---")