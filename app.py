#!/usr/bin/env python3
"""
🚀 Render Entry Point pour Arsenal V4 WebPanel
Point d'entrée simplifié pour le déploiement Render
"""
import sys
import os
from pathlib import Path

# Ajouter le chemin du webpanel
webpanel_path = Path(__file__).parent / "Arsenal_V4" / "webpanel"
sys.path.insert(0, str(webpanel_path))
sys.path.insert(0, str(webpanel_path / "backend"))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

print("🚀 Render Entry: Démarrage Arsenal V4 WebPanel...")

# Importer l'application depuis le webpanel
try:
    from backend.advanced_server import app
    print("✅ Render Entry: Application importée avec succès")
except ImportError as e:
    print(f"❌ Render Entry: Erreur import: {e}")
    raise

# Setup keep-alive
def setup_keep_alive():
    try:
        # Import depuis le répertoire webpanel
        webpanel_keep_alive = webpanel_path / "keep_alive.py"
        if webpanel_keep_alive.exists():
            sys.path.insert(0, str(webpanel_path))
            from keep_alive import set_app_url
            public_url = os.environ.get('RENDER_EXTERNAL_URL') or 'https://arsenal-webpanel.onrender.com'
            if 'onrender.com' in public_url:
                set_app_url(public_url)
                print(f"🎯 Keep-alive configuré pour: {public_url}")
    except Exception as e:
        print(f"⚠️ Keep-alive setup failed: {e}")

if __name__ == "__main__":
    setup_keep_alive()
    app.run(host="0.0.0.0", port=5000, debug=False)
else:
    setup_keep_alive()
    print("✅ Render Entry: Application prête pour Gunicorn")
