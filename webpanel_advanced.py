#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 ARSENAL V4 - WEBPANEL ULTRA-AVANCÉ
Panel de contrôle intégré avec authentification Discord et démarrage automatique du bot
"""

import os
import sys
import json
import sqlite3
import asyncio
import subprocess
import threading
import time
import secrets
import base64
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode, quote_plus

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_socketio import SocketIO, emit
import requests

# Configuration Discord OAuth
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '1346646498040877076')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://arsenal-webpanel.onrender.com/auth/callback')
BOT_TOKEN = os.getenv('DISCORD_TOKEN')

print(f"🔧 Discord OAuth Config:")
print(f"   CLIENT_ID: {DISCORD_CLIENT_ID}")
print(f"   CLIENT_SECRET: {'Défini' if DISCORD_CLIENT_SECRET else 'MANQUANT'}")
print(f"   REDIRECT_URI: {DISCORD_REDIRECT_URI}")
print(f"   BOT_TOKEN: {'Défini' if BOT_TOKEN else 'MANQUANT'}")

# Configuration Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = True if os.getenv('RENDER') else False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
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
            print("🤖 Démarrage du bot Discord...")
            print(f"🔧 Commande: {sys.executable} main.py")
            print(f"📁 Répertoire: {os.getcwd()}")
            
            # Vérifier que main.py existe
            if not os.path.exists("main.py"):
                return False, "Fichier main.py introuvable"
            
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
            print(f"🚀 Bot process PID: {self.bot_process.pid}")
            
            # Surveiller les logs en arrière-plan
            threading.Thread(target=self._monitor_bot_logs, daemon=True).start()
            
            return True, "Bot démarré avec succès"
            
        except Exception as e:
            print(f"❌ Erreur démarrage bot: {e}")
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

# Helper functions pour Discord API
def get_bot_guilds():
    """Récupère la liste des serveurs où le bot est présent"""
    if not BOT_TOKEN:
        return []
    
    try:
        headers = {
            'Authorization': f'Bot {BOT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://discord.com/api/v10/users/@me/guilds',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            bot_guilds = response.json()
            print(f"🤖 Bot présent sur {len(bot_guilds)} serveurs")
            return bot_guilds
        else:
            print(f"❌ Erreur récupération serveurs bot: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur API Discord bot: {e}")
        return []

def filter_user_servers(user_guilds, bot_guilds):
    """Filtre les serveurs de l'utilisateur pour afficher seulement ceux où le bot est présent"""
    if not bot_guilds:
        return []
    
    bot_guild_ids = {str(guild['id']) for guild in bot_guilds}
    filtered_servers = []
    
    for guild in user_guilds:
        if str(guild['id']) in bot_guild_ids:
            # Vérifier les permissions administrateur
            permissions = int(guild.get('permissions', 0))
            has_admin = (permissions & 0x8) != 0  # Administrator permission
            has_manage = (permissions & 0x20) != 0  # Manage server permission
            
            if has_admin or has_manage:
                guild['can_manage'] = True
                filtered_servers.append(guild)
    
    print(f"📊 Serveurs accessibles: {len(filtered_servers)}/{len(user_guilds)}")
    return filtered_servers

# Routes d'authentification Discord
@app.route('/login')
def login():
    """Page de connexion"""
    if 'user_info' in session:
        return redirect(url_for('dashboard'))
    
    # Créer un état de sécurité OAuth
    state = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    session['oauth_state'] = state
    
    # URL d'autorisation Discord
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize?"
        f"client_id={DISCORD_CLIENT_ID}&"
        f"redirect_uri={quote_plus(DISCORD_REDIRECT_URI)}&"
        f"response_type=code&"
        f"scope=identify+guilds&"
        f"state={state}"
    )
    
    print(f"🔑 Génération URL auth Discord: {discord_auth_url}")
    return render_template('login.html', auth_url=discord_auth_url)

@app.route('/auth/callback')
def auth_callback():
    """Callback d'authentification Discord"""
    try:
        # Vérifier l'état OAuth
        if 'oauth_state' not in session or request.args.get('state') != session['oauth_state']:
            print("❌ État OAuth invalide")
            return redirect(url_for('login'))
        
        code = request.args.get('code')
        if not code:
            print("❌ Code d'autorisation manquant")
            return redirect(url_for('login'))
        
        print(f"✅ Code reçu: {code[:20]}...")
        
        # Échanger le code contre un token
        token_data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        token_response = requests.post(
            'https://discord.com/api/v10/oauth2/token',
            data=token_data,
            headers=headers,
            timeout=10
        )
        
        if token_response.status_code != 200:
            print(f"❌ Erreur token Discord: {token_response.status_code}")
            return redirect(url_for('login'))
        
        token_info = token_response.json()
        access_token = token_info['access_token']
        print(f"✅ Token obtenu: {access_token[:20]}...")
        
        # Récupérer les informations utilisateur
        user_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        user_response = requests.get(
            'https://discord.com/api/v10/users/@me',
            headers=user_headers,
            timeout=10
        )
        
        guilds_response = requests.get(
            'https://discord.com/api/v10/users/@me/guilds',
            headers=user_headers,
            timeout=10
        )
        
        if user_response.status_code != 200 or guilds_response.status_code != 200:
            print("❌ Erreur récupération données utilisateur")
            return redirect(url_for('login'))
        
        user_data = user_response.json()
        user_guilds = guilds_response.json()
        
        print(f"👤 Utilisateur: {user_data['username']}")
        print(f"🏰 Serveurs utilisateur: {len(user_guilds)}")
        
        # Filtrer les serveurs où le bot est présent
        bot_guilds = get_bot_guilds()
        accessible_servers = filter_user_servers(user_guilds, bot_guilds)
        
        # Stocker les informations en session
        session['user_info'] = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'discriminator': user_data['discriminator'],
            'avatar': user_data.get('avatar'),
            'access_token': access_token,
            'guilds': accessible_servers,
            'guilds_count': len(accessible_servers)
        }
        
        # Nettoyer l'état OAuth
        session.pop('oauth_state', None)
        
        print(f"✅ Session créée pour {user_data['username']} - {len(accessible_servers)} serveurs accessibles")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for('login'))

# Routes Flask
@app.route('/')
def index():
    """Redirection vers dashboard ou login"""
    if 'user_info' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - Nécessite une authentification"""
    # Vérifier l'authentification
    if 'user_info' not in session:
        print("❌ Accès dashboard sans authentification - Redirection login")
        return redirect(url_for('login'))
    
    user_info = session['user_info']
    print(f"✅ Accès dashboard autorisé pour: {user_info['username']}")
    
    # Récupérer les stats du bot
    stats = panel.get_bot_stats()
    db_stats = panel.get_database_stats()
    
    # Préparer les données pour le template
    dashboard_data = {
        'user': user_info,
        'stats': stats,
        'db_stats': db_stats,
        'servers': user_info.get('guilds', []),
        'servers_count': user_info.get('guilds_count', 0)
    }
    
    return render_template('dashboard.html', **dashboard_data)

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
