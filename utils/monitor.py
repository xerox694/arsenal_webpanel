"""
🔍 Arsenal V4 - Système de Monitoring
Surveillance en temps réel du bot et du webpanel
"""

import psutil
import time
import json
import threading
from datetime import datetime

class ArsenalMonitor:
    def __init__(self):
        self.is_running = False
        self.stats = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_io': {'sent': 0, 'recv': 0},
            'bot_status': 'unknown',
            'webpanel_status': 'unknown',
            'uptime': 0,
            'last_update': None
        }
        
    def start_monitoring(self):
        """Démarrer le monitoring"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 Monitoring Arsenal démarré")
        
    def stop_monitoring(self):
        """Arrêter le monitoring"""
        self.is_running = False
        print("⏹️ Monitoring Arsenal arrêté")
        
    def _monitor_loop(self):
        """Boucle principale de monitoring"""
        start_time = time.time()
        
        while self.is_running:
            try:
                # CPU et mémoire
                self.stats['cpu_usage'] = psutil.cpu_percent(interval=1)
                self.stats['memory_usage'] = psutil.virtual_memory().percent
                self.stats['disk_usage'] = psutil.disk_usage('/').percent
                
                # Réseau
                net_io = psutil.net_io_counters()
                self.stats['network_io'] = {
                    'sent': net_io.bytes_sent,
                    'recv': net_io.bytes_recv
                }
                
                # Uptime
                self.stats['uptime'] = int(time.time() - start_time)
                self.stats['last_update'] = datetime.now().isoformat()
                
                # Vérifier les processus
                self._check_processes()
                
                # Sauvegarder les stats
                self._save_stats()
                
                time.sleep(5)  # Update toutes les 5 secondes
                
            except Exception as e:
                print(f"❌ Erreur monitoring: {e}")
                time.sleep(10)
                
    def _check_processes(self):
        """Vérifier l'état des processus Arsenal"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if any('arsenal' in str(arg).lower() for arg in proc.info['cmdline'] or []):
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        # Analyser les processus trouvés
        self.stats['bot_status'] = 'running' if any('main.py' in str(p['cmdline']) for p in processes) else 'stopped'
        self.stats['webpanel_status'] = 'running' if any('advanced_server.py' in str(p['cmdline']) for p in processes) else 'stopped'
        
    def _save_stats(self):
        """Sauvegarder les statistiques"""
        try:
            with open('logs/monitoring.json', 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"❌ Erreur sauvegarde stats: {e}")
            
    def get_stats(self):
        """Récupérer les statistiques actuelles"""
        return self.stats.copy()
        
    def get_formatted_stats(self):
        """Récupérer les stats formatées pour affichage"""
        stats = self.get_stats()
        
        return f"""
🔍 ARSENAL MONITORING - {stats['last_update'][:19]}

💻 SYSTÈME:
   CPU: {stats['cpu_usage']:.1f}%
   RAM: {stats['memory_usage']:.1f}%
   Disque: {stats['disk_usage']:.1f}%
   
🌐 RÉSEAU:
   Envoyé: {stats['network_io']['sent'] / 1024 / 1024:.1f} MB
   Reçu: {stats['network_io']['recv'] / 1024 / 1024:.1f} MB

🤖 SERVICES:
   Bot Discord: {stats['bot_status'].upper()}
   Webpanel: {stats['webpanel_status'].upper()}
   
⏱️ UPTIME: {stats['uptime'] // 3600}h {(stats['uptime'] % 3600) // 60}m {stats['uptime'] % 60}s
"""

# Instance globale
monitor = ArsenalMonitor()

if __name__ == "__main__":
    print("🚀 Arsenal Monitor - Test")
    monitor.start_monitoring()
    
    try:
        while True:
            print(monitor.get_formatted_stats())
            time.sleep(10)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("👋 Monitor arrêté")
