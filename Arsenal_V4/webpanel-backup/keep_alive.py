#!/usr/bin/env python3
"""
Arsenal V4 WebPanel - Keep Alive Service
Ping automatique pour éviter que l'app Render s'endorme
"""

import requests
import time
import threading
import logging
from datetime import datetime

# Configuration
PING_INTERVAL = 600  # 10 minutes
PING_URL = ""  # Sera mis à jour automatiquement

class KeepAlive:
    def __init__(self, url=None):
        self.url = url
        self.running = True
        
    def ping(self):
        """Ping l'application pour la garder active"""
        if not self.url:
            return False
            
        try:
            response = requests.get(f"{self.url}/health", timeout=30)
            print(f"[{datetime.now()}] ✅ Keep-alive ping: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Keep-alive failed: {e}")
            return False
    
    def start_pinging(self):
        """Démarre le service de ping automatique"""
        def ping_loop():
            while self.running:
                if self.url:
                    self.ping()
                time.sleep(PING_INTERVAL)
        
        thread = threading.Thread(target=ping_loop, daemon=True)
        thread.start()
        print(f"🚀 Keep-alive service started (ping every {PING_INTERVAL//60} minutes)")

# Instance globale
keep_alive = KeepAlive()

def set_app_url(url):
    """Configure l'URL de l'app pour le keep-alive"""
    keep_alive.url = url
    keep_alive.start_pinging()
