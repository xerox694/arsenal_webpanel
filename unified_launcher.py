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

import os
import sys
import threading
import time

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
    print("🤖 [BOT-THREAD] Démarrage du Bot Discord...")
    print(f"🔍 [BOT-THREAD] Thread actuel: {threading.current_thread().name}")
    
    try:
        # Ajouter le chemin principal
        bot_dir = os.path.dirname(__file__)
        if bot_dir not in sys.path:
            sys.path.insert(0, bot_dir)
        print(f"📁 [BOT-THREAD] Bot dir: {bot_dir}")
        
        # Changer vers le dossier du bot
        original_cwd = os.getcwd()
        os.chdir(bot_dir)
        print(f"🔍 [BOT-THREAD] Changement répertoire: {original_cwd} → {os.getcwd()}")
        
        print(f"🔍 [BOT-THREAD] Répertoire de travail: {os.getcwd()}")
        print(f"🔍 [BOT-THREAD] Fichiers dans le répertoire: {os.listdir('.')[:15]}")
        
        # Vérifier si main.py existe
        if not os.path.exists('main.py'):
            print("❌ [BOT-THREAD] main.py non trouvé!")
            print(f"🔍 [BOT-THREAD] Fichiers .py disponibles: {[f for f in os.listdir('.') if f.endswith('.py')]}")
            return
        
        print("✅ [BOT-THREAD] main.py trouvé")
        
        # Vérifier le token Discord
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            print("❌ [BOT-THREAD] DISCORD_TOKEN manquant - Bot non démarré")
            return
        
        print(f"✅ [BOT-THREAD] Token Discord présent (longueur: {len(discord_token)})")
        
        # Lire le contenu de main.py avant execution
        print("📄 [BOT-THREAD] Lecture du contenu de main.py...")
        with open('main.py', 'r', encoding='utf-8') as f:
            code_preview = f.read()[:500]  # Premiers 500 caractères
            print(f"📄 [BOT-THREAD] Aperçu main.py: {code_preview}...")
        
        # Exécuter main.py comme un script avec le bon contexte
        print("🚀 [BOT-THREAD] Exécution de main.py...")
        print("=" * 30)
        
        with open('main.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Créer le contexte d'exécution avec __name__ = "__main__"
        exec_globals = {
            '__name__': '__main__', 
            '__file__': os.path.abspath('main.py'),
            '__builtins__': __builtins__
        }
        
        print("⚡ [BOT-THREAD] Début exécution main.py...")
        exec(code, exec_globals)
        print("✅ [BOT-THREAD] main.py exécuté avec succès")
        
    except Exception as e:
        print(f"❌ [BOT-THREAD] Erreur Bot Discord: {e}")
        import traceback
        print(f"📋 [BOT-THREAD] Traceback complet:")
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
    print(f"  - Répertoire de travail: {os.getcwd()}")
    print(f"  - Fichiers disponibles: {os.listdir('.')[:15]}")
    
    if not discord_token:
        print("❌ DISCORD_TOKEN manquant!")
        print("Ajoutez votre token Discord dans les variables d'environnement Render")
        # Ne pas exit, juste démarrer le webpanel sans bot
        print("🌐 Démarrage WebPanel SEULEMENT...")
        start_webpanel()
        return
    
    print("✅ Configuration vérifiée")
    
    # Lancer le Bot Discord dans un thread séparé (en arrière-plan)
    print("🤖 Lancement du Bot Discord en arrière-plan...")
    print(f"📁 Vérification main.py existe: {os.path.exists('main.py')}")
    
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True, name="DiscordBotThread")
    bot_thread.start()
    print(f"✅ Thread bot créé: {bot_thread.name}")
    
    # Attendre que le bot démarre
    print("⏳ Attente du démarrage du Bot...")
    time.sleep(5)
    print(f"🔍 Thread bot status après 5s: {'🟢 Alive' if bot_thread.is_alive() else '🔴 Dead'}")
    
    if bot_thread.is_alive():
        print("✅ Bot Discord semble démarré")
    else:
        print("❌ Bot Discord n'a pas démarré correctement")
    
    # Lancer le WebPanel dans le thread principal (pour écouter sur PORT)
    print("🌐 Lancement du WebPanel sur PORT...")
    start_webpanel()

if __name__ == "__main__":
    main()
