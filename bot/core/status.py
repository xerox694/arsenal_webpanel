import json
import os
import datetime
from typing import Dict, Any

def update_bot_status(bot=None, **kwargs):
    """Met à jour le fichier de statut du bot pour l'API"""
    try:
        if bot and hasattr(bot, 'user') and bot.user and bot.is_ready():
            # Bot réel connecté
            uptime_seconds = (datetime.datetime.utcnow() - bot.startup_time).total_seconds()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime = f"{hours}h {minutes}m"
            
            status_data = {
                "online": True,
                "uptime": uptime,
                "latency": round(bot.latency * 1000) if bot.latency else 0,
                "servers_connected": len(bot.guilds),
                "users_connected": sum(guild.member_count or 0 for guild in bot.guilds),
                "status": "operational",
                "last_restart": bot.startup_time.strftime("%H:%M:%S"),
                "last_update": datetime.datetime.utcnow().isoformat()
            }
        else:
            # Status par défaut ou avec override
            status_data = {
                "online": kwargs.get('online', False),
                "uptime": kwargs.get('uptime', "0h 0m"),
                "latency": kwargs.get('latency', 0),
                "servers_connected": kwargs.get('servers_connected', 0),
                "users_connected": kwargs.get('users_connected', 0),
                "status": kwargs.get('status', "starting"),
                "last_restart": kwargs.get('last_restart', datetime.datetime.now().strftime("%H:%M:%S")),
                "last_update": datetime.datetime.utcnow().isoformat()
            }
        
        # Écrire le fichier de status
        with open('bot_status.json', 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
            
        print(f"[STATUS] Bot status updated: {status_data['status']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur mise à jour status: {e}")
        return False

def get_bot_status() -> Dict[str, Any]:
    """Récupère le statut actuel du bot"""
    try:
        if os.path.exists('bot_status.json'):
            with open('bot_status.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "online": False,
                "uptime": "0h 0m",
                "latency": 0,
                "servers_connected": 0,
                "users_connected": 0,
                "status": "offline",
                "last_restart": "N/A",
                "last_update": datetime.datetime.utcnow().isoformat()
            }
    except Exception as e:
        print(f"[ERROR] Erreur lecture status: {e}")
        return {"online": False, "status": "error"}
