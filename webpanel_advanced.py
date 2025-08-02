#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 ARSENAL V4 - WEBPANEL ULTRA-AVANCÉ
Panel de contrôle intégré avec démarrage automatique du bot
"""

import os
import sys
import json
import sqlite3
import asyncio
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_socketio import SocketIO, emit
import requests

# Configuration
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
bot_process = None
bot_status = "stopped"
bot_logs = []
MAX_LOGS = 1000

class ArsenalWebPanel:
    def __init__(self):
        self.bot_process = None
        self.bot_status = "stopped"
        self.bot_logs = []
        self.setup_directories()
        
    def setup_directories(self):
        """Créer les répertoires nécessaires"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        
    def get_bot_stats(self):
        """Récupérer les statistiques du bot"""
        stats = {
            "status": self.bot_status,
            "uptime": "N/A",
            "guilds": 0,
            "users": 0,
            "commands": 0,
            "modules": []
        }
        
        # Lire les logs pour extraire des infos
        try:
            if os.path.exists("logs/bot.log"):
                with open("logs/bot.log", "r", encoding="utf-8") as f:
                    logs = f.readlines()[-50:]  # Dernières 50 lignes
                    
                for log in logs:
                    if "Shard ID" in log and "connected" in log:
                        stats["status"] = "online"
                    elif "guilds" in log.lower():
                        # Extraire le nombre de serveurs si disponible
                        pass
                        
        except Exception as e:
            print(f"Erreur lecture stats: {e}")
            
        return stats
    
    def get_database_stats(self):
        """Statistiques des bases de données"""
        stats = {}
        
        # Arsenal V4 Database
        try:
            if os.path.exists("arsenal_v4.db"):
                conn = sqlite3.connect("arsenal_v4.db")
                cursor = conn.cursor()
                
                # Compter les utilisateurs
                cursor.execute("SELECT COUNT(*) FROM user_profiles")
                stats["user_profiles"] = cursor.fetchone()[0]
                
                # Compter les succès
                cursor.execute("SELECT COUNT(*) FROM user_achievements")
                stats["achievements"] = cursor.fetchone()[0]
                
                conn.close()
        except Exception as e:
            print(f"Erreur DB Arsenal: {e}")
            
        # Hunt Royal Database
        try:
            if os.path.exists("hunt_royal.db"):
                conn = sqlite3.connect("hunt_royal.db")
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM hunters")
                stats["hunters"] = cursor.fetchone()[0]
                
                conn.close()
        except Exception as e:
            print(f"Erreur DB Hunt Royal: {e}")
            
        return stats
    
    def start_bot(self):
        """Démarrer le bot Discord"""
        if self.bot_process and self.bot_process.poll() is None:
            return False, "Le bot est déjà en cours d'exécution"
            
        try:
            # Démarrer le bot en arrière-plan
            self.bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.bot_status = "starting"
            
            # Surveiller les logs en arrière-plan
            threading.Thread(target=self._monitor_bot_logs, daemon=True).start()
            
            return True, "Bot démarré avec succès"
            
        except Exception as e:
            return False, f"Erreur démarrage bot: {e}"
    
    def stop_bot(self):
        """Arrêter le bot Discord"""
        if not self.bot_process or self.bot_process.poll() is not None:
            return False, "Le bot n'est pas en cours d'exécution"
            
        try:
            self.bot_process.terminate()
            self.bot_process.wait(timeout=10)
            self.bot_status = "stopped"
            return True, "Bot arrêté avec succès"
            
        except subprocess.TimeoutExpired:
            self.bot_process.kill()
            self.bot_status = "stopped"
            return True, "Bot forcé à s'arrêter"
            
        except Exception as e:
            return False, f"Erreur arrêt bot: {e}"
    
    def restart_bot(self):
        """Redémarrer le bot Discord"""
        stop_success, stop_msg = self.stop_bot()
        if not stop_success:
            return False, f"Erreur arrêt: {stop_msg}"
            
        time.sleep(2)  # Attendre avant redémarrage
        
        start_success, start_msg = self.start_bot()
        return start_success, start_msg
    
    def _monitor_bot_logs(self):
        """Surveiller les logs du bot en temps réel"""
        if not self.bot_process:
            return
            
        for line in iter(self.bot_process.stdout.readline, ''):
            if line:
                self.bot_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "message": line.strip(),
                    "level": "INFO"
                })
                
                # Limiter le nombre de logs
                if len(self.bot_logs) > MAX_LOGS:
                    self.bot_logs = self.bot_logs[-MAX_LOGS//2:]
                
                # Émettre via WebSocket
                socketio.emit('bot_log', {
                    "timestamp": datetime.now().isoformat(),
                    "message": line.strip()
                })
                
                # Détecter le statut
                if "est prêt et en streaming" in line:
                    self.bot_status = "online"
                    socketio.emit('bot_status', {"status": "online"})
                    
        # Bot arrêté
        self.bot_status = "stopped"
        socketio.emit('bot_status', {"status": "stopped"})

# Instance du panel
panel = ArsenalWebPanel()

# Routes Flask
@app.route('/')
def dashboard():
    """Dashboard principal"""
    stats = panel.get_bot_stats()
    db_stats = panel.get_database_stats()
    return render_template('dashboard.html', stats=stats, db_stats=db_stats)

@app.route('/bot/start')
def start_bot():
    """Démarrer le bot"""
    success, message = panel.start_bot()
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('dashboard'))

@app.route('/bot/stop')
def stop_bot():
    """Arrêter le bot"""
    success, message = panel.stop_bot()
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('dashboard'))

@app.route('/bot/restart')
def restart_bot():
    """Redémarrer le bot"""
    success, message = panel.restart_bot()
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('dashboard'))

@app.route('/modules')
def modules():
    """Gestion des modules"""
    modules_list = [
        {
            "name": "AutoMod System",
            "status": "active",
            "description": "Système d'auto-modération avancé avec filtrage par niveaux",
            "commands": ["/automod status", "/automod toggle", "/automod config"]
        },
        {
            "name": "User Profiles",
            "status": "active", 
            "description": "Système de profils utilisateurs avec styles d'écriture",
            "commands": ["/profile view", "/profile config", "/profile test_style"]
        },
        {
            "name": "Hunt Royal",
            "status": "active",
            "description": "Système Hunt Royal avec base de données complète",
            "commands": ["/hunt search", "/hunt team", "/hunt update"]
        },
        {
            "name": "Economy System",
            "status": "active",
            "description": "Système économique avec XP, argent et boutique",
            "commands": ["/economy balance", "/economy daily", "/economy work"]
        },
        {
            "name": "Ticket System",
            "status": "active",
            "description": "Système de tickets avec catégories et logs",
            "commands": ["/ticket create", "/ticket close", "/ticket add"]
        },
        {
            "name": "Voice Hub",
            "status": "active",
            "description": "Salons vocaux temporaires automatiques",
            "commands": ["Gestion automatique"]
        }
    ]
    return render_template('modules.html', modules=modules_list)

@app.route('/logs')
def logs():
    """Logs du bot en temps réel"""
    return render_template('logs.html', logs=panel.bot_logs[-100:])

@app.route('/api/bot/status')
def api_bot_status():
    """API: Statut du bot"""
    return jsonify({
        "status": panel.bot_status,
        "process_running": panel.bot_process and panel.bot_process.poll() is None
    })

@app.route('/api/stats')
def api_stats():
    """API: Statistiques complètes"""
    return jsonify({
        "bot": panel.get_bot_stats(),
        "database": panel.get_database_stats(),
        "logs_count": len(panel.bot_logs)
    })

@app.route('/api/reload/<module_name>')
def api_reload_module(module_name):
    """API: Recharger un module"""
    # Ici on pourrait envoyer une commande au bot via WebSocket ou API
    return jsonify({
        "success": True,
        "message": f"Module {module_name} rechargé (simulation)"
    })

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Client connecté"""
    emit('bot_status', {"status": panel.bot_status})

@socketio.on('request_logs')
def handle_request_logs():
    """Demande des logs récents"""
    emit('logs_update', {"logs": panel.bot_logs[-50:]})

if __name__ == '__main__':
    import argparse
    
    # Parser des arguments
    parser = argparse.ArgumentParser(description='Arsenal V4 WebPanel')
    parser.add_argument('--start-bot', action='store_true', help='Démarrer automatiquement le bot')
    parser.add_argument('--host', default='0.0.0.0', help='Host pour le serveur web')
    parser.add_argument('--port', type=int, default=5000, help='Port pour le serveur web')
    parser.add_argument('--production', action='store_true', help='Mode production (optimisé pour Render/Heroku)')
    
    args = parser.parse_args()
    
    # Configuration pour mode production
    if args.production:
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        # Utiliser PORT environment variable si disponible (Render/Heroku)
        port = int(os.environ.get('PORT', args.port))
        host = args.host
        debug = False
        print("🚀 Arsenal V4 WebPanel - Mode Production")
        print(f"🌐 Render/Heroku deployment on port {port}")
    else:
        port = args.port
        host = args.host
        debug = False
        print("🌐 Arsenal V4 WebPanel starting...")
        print(f"📊 Dashboard: http://{host}:{port}")
    
    print("🔄 Bot auto-start available")
    
    # Démarrer automatiquement le bot si demandé
    if args.start_bot:
        print("🤖 Auto-starting bot...")
        panel.start_bot()
    
    # Lancer le serveur web
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )
