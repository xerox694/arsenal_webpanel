import os
import json
from core.logger import log

MEMORY_PATH = "data/memoire.json"
memoire = {}
exceptions = set()

def load_memoire():
    global memoire
    try:
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                memoire = json.load(f)
                log.info("🧠 memoire.json chargé")
        else:
            memoire = {}
            log.warning("⚠️ Aucun fichier memoire.json trouvé")
    except Exception as e:
        log.error(f"❌ Erreur lecture memoire.json : {e}")
        memoire = {}

def save_memoire():
    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memoire, f, indent=4)
            log.info("💾 Mémoire sauvegardée")
    except Exception as e:
        log.error(f"⚠️ Erreur sauvegarde mémoire : {e}")

def toggle_exception(command_name: str):
    if command_name in exceptions:
        exceptions.remove(command_name)
        return False
    else:
        exceptions.add(command_name)
        return True