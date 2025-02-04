import json
import os

PLAYER_DATA = "player_data.json"

def save_player(soldi, corrente):
    dati = {
        "monete": soldi,
        "corrente": corrente,
    }
    with open(PLAYER_DATA, "w+") as f:
        json.dump(dati, f)

def load_player():
    if not os.path.exists(PLAYER_DATA):
        return {"monete": 0, "corrente": "base"}
    with open(PLAYER_DATA, "r") as f:
        return json.load(f)

