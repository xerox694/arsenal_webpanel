#!/usr/bin/env python3
"""
🚀 Arsenal Simple Starter for Render
Lance le bot Discord ET le webpanel simultanément
"""

import os
import sys
import subprocess
import time
import threading
import signal

def log(msg):
    """Logger avec timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [ARSENAL] {msg}", flush=True)

def start_bot():
    """Démarrer le bot Discord en arrière-plan"""
    try:
        # Vérifier les prérequis
        if not os.environ.get('DISCORD_TOKEN'):
            log("❌ DISCORD_TOKEN manquant - Bot non démarré")
            return None
            
        if not os.path.exists('main.py'):
            log("❌ main.py manquant - Bot non démarré")
            return None
        
        log("🤖 Démarrage Bot Discord...")
        
        # Créer l'environnement pour le bot
        bot_env = os.environ.copy()
        bot_env['PYTHONUNBUFFERED'] = '1'
        
        # Lancer le bot
        bot_process = subprocess.Popen(
            [sys.executable, 'main.py'],
            env=bot_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        log(f"✅ Bot process démarré: PID {bot_process.pid}")
        
        # Monitorer le démarrage pendant 10 secondes
        for i in range(10):
            if bot_process.poll() is not None:
                # Le bot s'est arrêté
                stdout, _ = bot_process.communicate()
                log(f"❌ Bot terminé prématurément")
                log(f"Output: {stdout[:500]}...")
                return None
            time.sleep(1)
        
        log("✅ Bot semble démarré avec succès!")
        return bot_process
        
    except Exception as e:
        log(f"❌ Erreur démarrage bot: {e}")
        return None

def monitor_bot(bot_process):
    """Monitorer le bot et redémarrer si nécessaire"""
    if not bot_process:
        return
        
    log("🔍 Monitoring du bot démarré")
    
    try:
        while True:
            time.sleep(30)  # Vérifier toutes les 30s
            
            if bot_process.poll() is not None:
                log("❌ Bot s'est arrêté, tentative de redémarrage...")
                bot_process = start_bot()
                if not bot_process:
                    log("❌ Impossible de redémarrer le bot")
                    break
    except Exception as e:
        log(f"❌ Erreur monitoring: {e}")

def main():
    """Point d'entrée principal"""
    log("🚀 Arsenal Simple Starter démarré")
    log(f"🔧 Python version: {sys.version}")
    log(f"📁 Working directory: {os.getcwd()}")
    
    # Vérifier les fichiers essentiels
    essential_files = ['main.py', 'advanced_server.py']
    for file in essential_files:
        if os.path.exists(file):
            log(f"✅ {file} trouvé")
        else:
            log(f"❌ {file} manquant")
    
    # Variables d'environnement importantes
    log(f"🔑 DISCORD_TOKEN: {'✅ Présent' if os.environ.get('DISCORD_TOKEN') else '❌ Manquant'}")
    log(f"🌍 PORT: {os.environ.get('PORT', '10000')}")
    
    # Démarrer le bot Discord en arrière-plan
    bot_process = start_bot()
    
    if bot_process:
        # Démarrer le monitoring en thread
        monitor_thread = threading.Thread(target=monitor_bot, args=(bot_process,), daemon=True)
        monitor_thread.start()
        log("✅ Bot monitoring activé")
    else:
        log("⚠️ Bot non démarré - continuer avec webpanel seulement")
    
    # Attendre un peu
    time.sleep(2)
    
    # Démarrer le webpanel (bloquant)
    log("🌐 Démarrage WebPanel...")
    
    try:
        # Configurer l'environnement Flask
        os.environ.setdefault('FLASK_ENV', 'production')
        os.environ.setdefault('PYTHONUNBUFFERED', '1')
        
        # Lancer advanced_server.py directement
        import advanced_server
        
        # Le serveur se lance automatiquement
        log("✅ WebPanel démarré via import")
        
    except Exception as e:
        log(f"❌ Erreur webpanel: {e}")
        
        # Fallback: lancer en subprocess
        try:
            log("🔄 Fallback: Lancement webpanel en subprocess...")
            subprocess.run([sys.executable, 'advanced_server.py'])
        except Exception as e2:
            log(f"❌ Erreur fallback: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("👋 Arrêt demandé")
        sys.exit(0)
    except Exception as e:
        log(f"❌ Erreur critique: {e}")
        sys.exit(1)
