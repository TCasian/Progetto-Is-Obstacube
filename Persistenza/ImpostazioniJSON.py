import json
import os

SETTINGS_FILE = "settings.json"
PLAYER_DATA = "player_data.json"

def save_settings(fullscreen: bool, audio: bool):
    settings = {
        "fullscreen": "si" if fullscreen else "no",
        "audio": "si" if audio else "no"
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"fullscreen": "no", "audio": "si"}  # Valori di default
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


def save_player(skins, soldi, corrente):
    dati = {
        "skins": skins,
        "soldi": soldi,
        "corrente": corrente,
    }
    with open(PLAYER_DATA, "w+") as f:
        json.dump(dati, f)

def load_player():
    if not os.path.exists(PLAYER_DATA):
        return {"skins": "", "soldi": 0, "corrente": "base"}
    with open(PLAYER_DATA, "r") as f:
        return json.load(f)