#!/usr/bin/env python3
"""
🚀 WSGI Entry Point pour Arsenal V4 WebPanel
Configuration de production pour serveurs web
"""
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_path / "backend"))

# Configuration de production désactivée - utilise uniquement les variables d'environnement Render
# Le fichier production_config.json ne doit PAS écraser les vraies variables d'environnement

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Importer l'application
from backend.app import app as application, socketio
from keep_alive import set_app_url

# Setup keep-alive après démarrage
def setup_keep_alive():
    try:
        public_url = os.environ.get('RENDER_EXTERNAL_URL')
        if public_url and 'onrender.com' in public_url:
            set_app_url(public_url)
            print(f"🎯 Keep-alive configuré pour: {public_url}")
    except Exception as e:
        print(f"⚠️ Keep-alive setup failed: {e}")

if __name__ == "__main__":
    setup_keep_alive()
    # Pour le développement local avec WebSocket
    socketio.run(application, host="0.0.0.0", port=5000, debug=False)
else:
    # Pour Render/production avec WebSocket
    setup_keep_alive()
