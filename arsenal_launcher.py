"""
🚀 Arsenal Launcher Ultra Robuste
Lance le webpanel ET le bot Discord de manière fiable
"""

import os
import sys
import subprocess
import time
import signal
import threading
import json
from datetime import datetime

class ArsenalLauncher:
    def __init__(self):
        self.webpanel_process = None
        self.bot_process = None
        self.running = True
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def start_webpanel(self):
        """Démarrer le webpanel Flask"""
        try:
            self.log("🌐 Démarrage WebPanel...")
            
            self.webpanel_process = subprocess.Popen(
                [sys.executable, 'advanced_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log(f"✅ WebPanel démarré: PID {self.webpanel_process.pid}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur WebPanel: {e}")
            return False
    
    def start_bot(self):
        """Démarrer le bot Discord"""
        try:
            self.log("🤖 Démarrage Bot Discord...")
            
            # Vérifier le token
            discord_token = os.environ.get('DISCORD_TOKEN')
            if not discord_token:
                self.log("❌ DISCORD_TOKEN manquant")
                return False
                
            # Vérifier main.py
            if not os.path.exists('main.py'):
                self.log("❌ main.py non trouvé")
                return False
            
            # Créer environnement
            bot_env = os.environ.copy()
            
            self.bot_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                env=bot_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log(f"✅ Bot démarré: PID {self.bot_process.pid}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur Bot: {e}")
            return False
    
    def monitor_processes(self):
        """Monitorer les processus"""
        while self.running:
            try:
                # Vérifier webpanel
                if self.webpanel_process and self.webpanel_process.poll() is not None:
                    self.log("❌ WebPanel arrêté, redémarrage...")
                    self.start_webpanel()
                
                # Vérifier bot
                if self.bot_process and self.bot_process.poll() is not None:
                    self.log("❌ Bot arrêté, redémarrage...")
                    self.start_bot()
                
                # Créer fichier de statut
                self.update_status()
                
                time.sleep(30)  # Vérifier toutes les 30s
                
            except Exception as e:
                self.log(f"❌ Erreur monitoring: {e}")
                time.sleep(10)
    
    def update_status(self):
        """Mettre à jour le fichier de statut"""
        try:
            status = {
                "webpanel": {
                    "running": self.webpanel_process and self.webpanel_process.poll() is None,
                    "pid": self.webpanel_process.pid if self.webpanel_process else None
                },
                "bot": {
                    "running": self.bot_process and self.bot_process.poll() is None,
                    "pid": self.bot_process.pid if self.bot_process else None
                },
                "last_update": datetime.now().isoformat()
            }
            
            with open('launcher_status.json', 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.log(f"❌ Erreur update status: {e}")
    
    def cleanup(self):
        """Nettoyer les processus"""
        self.log("🛑 Arrêt des processus...")
        self.running = False
        
        if self.webpanel_process:
            try:
                self.webpanel_process.terminate()
                self.webpanel_process.wait(timeout=5)
            except:
                self.webpanel_process.kill()
        
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            except:
                self.bot_process.kill()
    
    def run(self):
        """Lancer Arsenal complet"""
        try:
            self.log("🚀 Arsenal Launcher démarré")
            
            # Démarrer les services
            webpanel_ok = self.start_webpanel()
            time.sleep(2)  # Laisser le webpanel s'initialiser
            
            bot_ok = self.start_bot()
            
            if not webpanel_ok:
                self.log("❌ WebPanel n'a pas démarré")
                return False
            
            self.log(f"📊 Services: WebPanel={'✅' if webpanel_ok else '❌'} Bot={'✅' if bot_ok else '❌'}")
            
            # Démarrer le monitoring
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            # Attendre indéfiniment (pour Render)
            while self.running:
                time.sleep(1)
            
        except KeyboardInterrupt:
            self.log("👋 Arrêt demandé")
        except Exception as e:
            self.log(f"❌ Erreur critique: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    launcher = ArsenalLauncher()
    
    # Gérer les signaux d'arrêt
    def signal_handler(signum, frame):
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    launcher.run()
