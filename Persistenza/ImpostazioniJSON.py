import json
import os

SETTINGS_FILE = "settings.json"

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