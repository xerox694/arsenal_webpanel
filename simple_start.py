#!/usr/bin/env python3
"""
🚀 Arsenal Simple Starter
Script de démarrage simple pour Render
"""

import os
import sys
import subprocess
import time
import threading

def log(msg):
    print(f"[ARSENAL] {msg}", flush=True)

def start_bot():
    """Démarrer le bot Discord en arrière-plan"""
    try:
        if not os.environ.get('DISCORD_TOKEN'):
            log("❌ DISCORD_TOKEN manquant - Bot non démarré")
            return
            
        if not os.path.exists('main.py'):
            log("❌ main.py manquant - Bot non démarré")
            return
        
        log("🤖 Démarrage Bot Discord...")
        
        # Lancer le bot
        bot_process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        log(f"✅ Bot process créé: PID {bot_process.pid}")
        
        # Monitorer pendant 5 secondes
        for i in range(5):
            if bot_process.poll() is not None:
                stdout, stderr = bot_process.communicate()
                log(f"❌ Bot terminé prématurément")
                log(f"STDOUT: {stdout.decode()[:200]}...")
                log(f"STDERR: {stderr.decode()[:200]}...")
                return
            time.sleep(1)
        
        log("✅ Bot semble démarré avec succès!")
        
    except Exception as e:
        log(f"❌ Erreur bot: {e}")

def main():
    log("🚀 Arsenal Simple Starter démarré")
    
    # Démarrer le bot en arrière-plan
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Attendre un peu
    time.sleep(3)
    
    # Démarrer le webpanel (bloquant)
    log("🌐 Démarrage WebPanel...")
    
    try:
        # Importer et lancer le webpanel
        os.environ.setdefault('FLASK_ENV', 'production')
        
        # Lancer advanced_server.py
        subprocess.run([sys.executable, 'advanced_server.py'])
        
    except Exception as e:
        log(f"❌ Erreur webpanel: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
