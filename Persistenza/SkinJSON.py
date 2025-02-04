import json
import os

SKIN_DATA = "skin.json"

def load_skins():
    """
        Legge le skin dal file JSON. Se il file non esiste, lo crea con i valori di default.
        Restituisce una lista di dizionari con le informazioni delle skin.
        """
    # Configurazione iniziale di default
    default_skins = [
        {"nome": "base", "costo": 0, "acquistata": True},
        {"nome": "paurosa", "costo": 100, "acquistata": False},
        {"nome": "pietro", "costo": 150, "acquistata": False},
        {"nome": "rainbow", "costo": 200, "acquistata": False},
        {"nome": "zombie", "costo": 250, "acquistata": False}
    ]

    if not os.path.exists(SKIN_DATA):
        # Crea il file con le skin di default
        with open(SKIN_DATA, 'w') as f:
            json.dump(default_skins, f, indent=4)
        return default_skins
    else:
        # Legge il file esistente
        with open(SKIN_DATA, 'r') as f:
            return json.load(f)

def save_skins(skins):
    """
        Scrive la lista aggiornata delle skin nel file JSON
        """
    with open(SKIN_DATA, 'w') as f:
        json.dump(skins, f, indent=4)

def add_skin(nome):
    skins = load_skins()
    skins.append({"nome": nome, "costo": 100, "acquistata": False})
    save_skins(skins)