import json
import os
from core.logger import log

CONFIG_PATH = "data/config.json"
config_data = {}

def load_config():
    global config_data
    if not os.path.exists(CONFIG_PATH):
        log.warning("📁 config.json introuvable, création...")
        config_data = {}
        save_config()
        return

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            log.info("✅ config.json chargé")
    except Exception as e:
        log.error(f"❌ Erreur lecture config.json : {e}")
        config_data = {}

def save_config():
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
            log.info("💾 Configuration sauvegardée")
    except Exception as e:
        log.error(f"⚠️ Erreur sauvegarde config : {e}")