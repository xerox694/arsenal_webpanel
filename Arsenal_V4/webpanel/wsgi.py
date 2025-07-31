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

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

print("🚀 WSGI: Démarrage Arsenal V4 WebPanel...")

# Importer l'application depuis advanced_server
try:
    from backend.advanced_server import app as application
    print("✅ WSGI: Application importée depuis advanced_server.py")
except ImportError as e:
    print(f"❌ WSGI: Erreur import advanced_server: {e}")
    raise

# Setup keep-alive après démarrage
def setup_keep_alive():
    try:
        from keep_alive import set_app_url
        public_url = os.environ.get('RENDER_EXTERNAL_URL') or 'https://arsenal-webpanel.onrender.com'
        if 'onrender.com' in public_url:
            set_app_url(public_url)
            print(f"🎯 Keep-alive configuré pour: {public_url}")
    except Exception as e:
        print(f"⚠️ Keep-alive setup failed: {e}")

if __name__ == "__main__":
    setup_keep_alive()
    # Pour le développement local
    application.run(host="0.0.0.0", port=5000, debug=False)
else:
    # Pour Render/production
    setup_keep_alive()
    print("✅ WSGI: Application prête pour Gunicorn")
