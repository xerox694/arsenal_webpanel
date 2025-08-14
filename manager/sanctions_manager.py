import json
import os
from core.logger import log

SANCTIONS_PATH = "data/sanctions.json"
sanctions = {}

def load_sanctions():
    global sanctions
    try:
        if os.path.exists(SANCTIONS_PATH):
            with open(SANCTIONS_PATH, "r", encoding="utf-8") as f:
                sanctions = json.load(f)
                log.info("📁 sanctions.json chargé avec succès")
        else:
            sanctions = {}
            log.warning("⚠️ sanctions.json introuvable — initialisation vide")
    except Exception as e:
        log.error(f"❌ Erreur lecture sanctions : {e}")
        sanctions = {}

def save_sanctions():
    try:
        with open(SANCTIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(sanctions, f, indent=4)
            log.info("💾 Casier sanctions sauvegardé")
    except Exception as e:
        log.error(f"❌ Échec sauvegarde casier : {e}")

def add_sanction(user_id: int, type_: str, raison: str, auteur: str, statut="active", expiration=None, durée=None, mode="manuel"):
    from datetime import datetime

    sanction = {
        "type": type_,
        "raison": raison,
        "auteur": auteur,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "statut": statut,
        "expiration": expiration,
        "durée": durée,
        "mode": mode
    }

    sanctions.setdefault(str(user_id), []).append(sanction)
    save_sanctions()