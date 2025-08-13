import json
import os
from typing import Dict, Any

# Configuration par défaut
DEFAULT_CONFIG = {
    "general": {
        "prefix": "!",
        "activity_type": "watching",
        "activity_name": "Arsenal V4.2.1",
        "status": "online"
    },
    "features": {
        "music": True,
        "moderation": True,
        "economy": True,
        "hunt_royal": True
    },
    "limits": {
        "max_queue_size": 50,
        "max_volume": 100,
        "timeout_duration": 300
    }
}

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config_data = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Créer le fichier avec la config par défaut
                self.save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"[ERROR] Erreur chargement config: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """Sauvegarde la configuration"""
        try:
            data = config_data or self.config_data
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] Erreur sauvegarde config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Récupère une valeur de config avec notation pointée"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Définit une valeur de config avec notation pointée"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()

# Instance globale
config_manager = ConfigManager()
config_data = config_manager.config_data

def load_config():
    """Recharge la configuration"""
    global config_data
    config_data = config_manager.load_config()
    return config_data

def save_config(data=None):
    """Sauvegarde la configuration"""
    return config_manager.save_config(data)

def get_config(key, default=None):
    """Récupère une valeur de config"""
    return config_manager.get(key, default)

def set_config(key, value):
    """Définit une valeur de config"""
    config_manager.set(key, value)
