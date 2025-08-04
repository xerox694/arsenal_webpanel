#!/usr/bin/env python3
"""
🚀 Render Entry Point pour Arsenal V4 WebPanel
Point d'entrée simplifié pour le déploiement Render
"""
import sys
import os
import time
import requests
import threading
from pathlib import Path

# Ajouter le chemin du webpanel
webpanel_path = Path(__file__).parent / "Arsenal_V4" / "webpanel"
sys.path.insert(0, str(webpanel_path))
sys.path.insert(0, str(webpanel_path / "backend"))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

print("🚀 Render Entry: Démarrage Arsenal V4 WebPanel...")

# Configuration pour Render
os.environ['PRODUCTION'] = 'True'
os.environ['RENDER_DEPLOYMENT'] = 'True'

# Importer l'application depuis le webpanel
try:
    from backend.advanced_server import app
    print("✅ Render Entry: Application importée avec succès")
    
    # Vérifier que nos nouvelles routes sont bien ajoutées
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    specialized_routes = ['/games-ultimate', '/ai-center', '/music-center', '/economy-center']
    for route in specialized_routes:
        if route in routes:
            print(f"✅ Route {route} trouvée")
        else:
            print(f"❌ Route {route} manquante")
    
except ImportError as e:
    print(f"❌ Render Entry: Erreur import: {e}")
    raise

# Service Keep-alive pour Render
def keep_alive_service():
    """Service de keep-alive pour maintenir l'application active"""
    def ping_app():
        url = os.environ.get('RENDER_EXTERNAL_URL', 'https://arsenal-webpanel.onrender.com')
        if 'onrender.com' in url:
            try:
                response = requests.get(f"{url}/health", timeout=30)
                if response.status_code == 200:
                    print(f"✅ Keep-alive ping: {response.status_code}")
                else:
                    print(f"⚠️ Keep-alive ping: {response.status_code}")
            except Exception as e:
                print(f"❌ Keep-alive error: {e}")
    
    while True:
        time.sleep(600)  # Ping toutes les 10 minutes
        ping_app()

# Démarrer keep-alive en arrière-plan
if os.environ.get('RENDER_EXTERNAL_URL'):
    keep_alive_thread = threading.Thread(target=keep_alive_service, daemon=True)
    keep_alive_thread.start()
    print("🚀 Keep-alive service started (ping every 10 minutes)")
    
    # URL pour le keep-alive
    app_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://arsenal-webpanel.onrender.com')
    print(f"🎯 Keep-alive configuré pour: {app_url}")

print("✅ Render Entry: Application prête pour Gunicorn")
