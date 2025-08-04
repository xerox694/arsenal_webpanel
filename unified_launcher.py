#!/usr/bin/env python3
"""
🚀 Arsenal V4 - Bot Discord + WebPanel Unified
Lance le bot Discord ET le WebPanel en parallèle sur Render
"""

import os
import sys
import threading
import time
import subprocess
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def start_webpanel():
    """Lance le WebPanel Flask"""
    print("🌐 Démarrage du WebPanel...")
    try:
        # Ajouter le chemin du webpanel
        webpanel_dir = os.path.join(os.path.dirname(__file__), 'Arsenal_V4', 'webpanel', 'backend')
        if webpanel_dir not in sys.path:
            sys.path.insert(0, webpanel_dir)
        
        # Changer le répertoire de travail
        original_cwd = os.getcwd()
        os.chdir(webpanel_dir)
        
        # Importer et lancer le serveur
        import advanced_server
        
        # Récupérer l'app Flask
        app = advanced_server.app
        
        # Configuration pour Render
        port = int(os.environ.get("PORT", 10000))
        host = "0.0.0.0"
        
        print(f"🌐 WebPanel démarré sur {host}:{port}")
        app.run(host=host, port=port, debug=False, threaded=True)
        
    except Exception as e:
        print(f"❌ Erreur WebPanel: {e}")
        import traceback
        traceback.print_exc()

def start_discord_bot():
    """Lance le bot Discord"""
    print("🤖 Démarrage du Bot Discord...")
    try:
        # Ajouter le chemin principal
        bot_dir = os.path.dirname(__file__)
        if bot_dir not in sys.path:
            sys.path.insert(0, bot_dir)
        
        # Changer vers le dossier du bot
        os.chdir(bot_dir)
        
        # Importer et exécuter le main du bot
        import main
        
    except Exception as e:
        print(f"❌ Erreur Bot Discord: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Point d'entrée principal"""
    print("🚀 Arsenal V4 Unified - Bot + WebPanel")
    print("=" * 50)
    
    # Vérifier les variables d'environnement essentielles
    discord_token = os.getenv("DISCORD_TOKEN")
    port = os.getenv("PORT", "10000")
    
    print(f"🔍 Variables d'environnement:")
    print(f"  - DISCORD_TOKEN: {'✅ Présent' if discord_token else '❌ Manquant'}")
    print(f"  - PORT: {port}")
    
    if not discord_token:
        print("❌ DISCORD_TOKEN manquant!")
        print("Ajoutez votre token Discord dans les variables d'environnement Render")
        sys.exit(1)
    
    print("✅ Configuration vérifiée")
    
    # Lancer le WebPanel dans un thread séparé
    print("🌐 Lancement du WebPanel en arrière-plan...")
    webpanel_thread = threading.Thread(target=start_webpanel, daemon=True)
    webpanel_thread.start()
    
    # Attendre que le WebPanel démarre
    print("⏳ Attente du démarrage du WebPanel...")
    time.sleep(5)
    
    # Lancer le bot Discord dans le thread principal
    print("🤖 Lancement du Bot Discord...")
    start_discord_bot()

if __name__ == "__main__":
    main()
