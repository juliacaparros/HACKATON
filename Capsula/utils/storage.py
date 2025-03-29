import json
import os

HISTORIAL_PATH = 'data/historial.json'

def cargar_historial():
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_historial(historial):
    with open(HISTORIAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)
