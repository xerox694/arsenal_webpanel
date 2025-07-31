import json
import os
from core.logger import log

ECONOMY_PATH = "data/economie.json"
balances = {}

def load_economy():
    global balances
    try:
        if os.path.exists(ECONOMY_PATH):
            with open(ECONOMY_PATH, "r", encoding="utf-8") as f:
                balances = json.load(f)
                log.info("💰 economie.json chargé")
        else:
            balances = {}
            log.warning("⚠️ economie.json absent — initialisation vide")
    except Exception as e:
        log.error(f"❌ Erreur lecture economy : {e}")
        balances = {}

def save_economy():
    try:
        with open(ECONOMY_PATH, "w", encoding="utf-8") as f:
            json.dump(balances, f, indent=4)
            log.info("💾 Données économiques sauvegardées")
    except Exception as e:
        log.error(f"⚠️ Erreur sauvegarde économie : {e}")

def get_balance(user_id: int) -> int:
    return balances.get(str(user_id), 0)

def update_balance(user_id: int, amount: int):
    balances[str(user_id)] = get_balance(user_id) + amount
    save_economy()