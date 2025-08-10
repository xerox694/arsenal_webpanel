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
        
        print(f"🔍 Répertoire de travail: {os.getcwd()}")
        print(f"🔍 Fichiers dans le répertoire: {os.listdir('.')[:10]}")  # Afficher les 10 premiers
        
        # Vérifier si main.py existe
        if not os.path.exists('main.py'):
            print("❌ main.py non trouvé!")
            return
        
        print("📁 main.py trouvé, tentative d'import...")
        
        # Vérifier le token Discord
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            print("❌ DISCORD_TOKEN manquant - Bot non démarré")
            return
        
        print("✅ Token Discord présent, lancement du bot...")
        
        # Exécuter main.py comme un script
        print("🚀 Exécution de main.py...")
        exec(open('main.py').read())
        
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
    
    # Lancer le Bot Discord dans un thread séparé (en arrière-plan)
    print("🤖 Lancement du Bot Discord en arrière-plan...")
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
    bot_thread.start()
    
    # Attendre que le bot démarre
    print("⏳ Attente du démarrage du Bot...")
    time.sleep(3)
    
    # Lancer le WebPanel dans le thread principal (pour écouter sur PORT)
    print("🌐 Lancement du WebPanel sur PORT...")
    start_webpanel()

if __name__ == "__main__":
    main()
