#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL V4 ULTIMATE - SERVEUR UNIFIÉ
========================================

Service unique qui lance:
- 🤖 Bot Discord Arsenal V4
- 🌐 WebPanel avec toutes les fonctionnalités
- 📊 Tableau de bord intégré
- 🎮 Modules Gaming, AI, Music, Economy dans la sidebar

Author: Arsenal V4 Team
Version: 4.2.1 ULTIMATE
"""

import os
import sys
import json
import asyncio
import threading
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Flask & WebSocket
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Variables d'environnement
os.environ.setdefault('PYTHONPATH', str(Path(__file__).parent))

# Configuration
print("🚀 Arsenal V4 Ultimate - Serveur Unifié")
print("=" * 50)

# Configuration Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'arsenal_v4_ultimate_key')
app.config['DEBUG'] = True
CORS(app, origins='*')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# Variables globales
bot_process = None
bot_status = "stopped"
real_time_stats = {
    'servers': 0,
    'users': 0,
    'commands_today': 0,
    'uptime': '0s'
}

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def home():
    """Page d'accueil - Redirection vers dashboard"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal intégré"""
    return render_template('dashboard.html')

# ==================== API ROUTES ====================

@app.route('/api/bot/status')
def bot_status_api():
    """API - Statut du bot"""
    global bot_process, bot_status
    
    if bot_process and bot_process.poll() is None:
        status = "online"
    else:
        status = "offline"
    
    return jsonify({
        'status': status,
        'uptime': real_time_stats['uptime'],
        'servers': real_time_stats['servers'],
        'users': real_time_stats['users'],
        'commands_today': real_time_stats['commands_today']
    })

@app.route('/api/bot/start', methods=['POST'])
def start_bot_api():
    """API - Démarrer le bot"""
    success, message = start_discord_bot()
    return jsonify({'success': success, 'message': message})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot_api():
    """API - Arrêter le bot"""
    success, message = stop_discord_bot()
    return jsonify({'success': success, 'message': message})

@app.route('/api/stats/real-time')
def real_time_stats_api():
    """API - Statistiques temps réel"""
    return jsonify(real_time_stats)

# ==================== STATIC FILES ====================

@app.route('/css/<path:filename>')
def css_files(filename):
    """Servir les fichiers CSS"""
    css_dir = Path(__file__).parent / 'Arsenal_V4' / 'webpanel' / 'frontend' / 'css'
    return send_from_directory(css_dir, filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    """Servir les fichiers JavaScript"""
    js_dir = Path(__file__).parent / 'Arsenal_V4' / 'webpanel' / 'frontend' / 'js'
    return send_from_directory(js_dir, filename)

@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir les fichiers statiques"""
    static_dir = Path(__file__).parent / 'static'
    return send_from_directory(static_dir, filename)

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Nouvelle connexion WebSocket"""
    print(f"🔗 Nouvelle connexion WebSocket")
    emit('welcome', {'message': 'Arsenal V4 Ultimate connecté!'})

@socketio.on('request_bot_status')
def handle_bot_status_request():
    """Demande de statut du bot"""
    emit('bot_status_update', {
        'status': bot_status,
        'stats': real_time_stats
    })

# ==================== GESTION DU BOT DISCORD ====================

def start_discord_bot():
    """Démarrer le bot Discord Arsenal V4"""
    global bot_process, bot_status
    
    try:
        print("🤖 Démarrage du Bot Discord Arsenal V4...")
        
        # Vérifier le token Discord
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            return False, "❌ DISCORD_TOKEN manquant dans les variables d'environnement"
        
        # Chemin vers le bot
        bot_dir = Path(__file__).parent / 'Arsenal_V4' / 'bot'
        bot_main = bot_dir / 'main.py'
        
        if not bot_main.exists():
            return False, f"❌ Fichier bot non trouvé: {bot_main}"
        
        # Environnement
        env = os.environ.copy()
        env['DISCORD_TOKEN'] = discord_token
        env['PYTHONPATH'] = str(bot_dir.parent)
        
        # Démarrer le processus bot
        bot_process = subprocess.Popen(
            [sys.executable, str(bot_main)],
            cwd=str(bot_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        bot_status = "starting"
        print(f"✅ Bot démarré avec PID: {bot_process.pid}")
        
        # Surveiller les logs
        threading.Thread(target=monitor_bot_logs, daemon=True).start()
        
        return True, "🚀 Bot Discord démarré avec succès!"
        
    except Exception as e:
        print(f"❌ Erreur démarrage bot: {e}")
        return False, f"Erreur: {e}"

def stop_discord_bot():
    """Arrêter le bot Discord"""
    global bot_process, bot_status
    
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process.wait(timeout=10)
            bot_status = "stopped"
            print("🛑 Bot Discord arrêté")
            return True, "Bot arrêté avec succès"
        else:
            return False, "Bot déjà arrêté"
    except Exception as e:
        return False, f"Erreur arrêt bot: {e}"

def monitor_bot_logs():
    """Surveiller les logs du bot en temps réel"""
    global bot_process, bot_status, real_time_stats
    
    if not bot_process:
        return
    
    print("📊 Surveillance des logs du bot démarrée...")
    
    for line in iter(bot_process.stdout.readline, ''):
        if line:
            line = line.strip()
            print(f"[BOT] {line}")
            
            # Analyser les logs pour extraire les stats
            if "Connecté en tant que" in line:
                bot_status = "online"
                socketio.emit('bot_status_update', {
                    'status': 'online',
                    'message': 'Bot connecté!'
                })
            
            elif "serveurs" in line.lower():
                try:
                    # Extraire le nombre de serveurs
                    import re
                    servers = re.findall(r'(\d+)', line)
                    if servers:
                        real_time_stats['servers'] = int(servers[0])
                except:
                    pass
    
    # Bot s'est arrêté
    bot_status = "stopped"
    print("❌ Bot Discord déconnecté")

def update_stats_loop():
    """Boucle de mise à jour des statistiques"""
    global real_time_stats
    
    start_time = datetime.now()
    
    while True:
        try:
            # Calculer l'uptime
            uptime_delta = datetime.now() - start_time
            hours = uptime_delta.seconds // 3600
            minutes = (uptime_delta.seconds % 3600) // 60
            real_time_stats['uptime'] = f"{uptime_delta.days}j {hours}h {minutes}m"
            
            # Envoyer les stats via WebSocket
            socketio.emit('stats_update', real_time_stats)
            
            time.sleep(30)  # Mise à jour toutes les 30 secondes
            
        except Exception as e:
            print(f"❌ Erreur mise à jour stats: {e}")
            time.sleep(30)

# ==================== TEMPLATES INTÉGRÉS ====================

def create_templates():
    """Créer les templates nécessaires"""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Template index.html
    index_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arsenal V4 Ultimate - Accueil</title>
    <style>
        body {
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: white;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
        }
        .container {
            max-width: 600px;
            padding: 2rem;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #00fff7, #ff006e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .btn {
            display: inline-block;
            padding: 1rem 2rem;
            background: linear-gradient(45deg, #00fff7, #ff006e);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            margin: 1rem;
            transition: transform 0.3s;
        }
        .btn:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Arsenal V4 Ultimate</h1>
        <p>Le bot Discord le plus avancé au monde</p>
        <a href="/dashboard" class="btn">🎮 Accéder au Dashboard</a>
    </div>
</body>
</html>'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # Créer un lien symbolique vers dashboard.html
    dashboard_source = Path(__file__).parent / 'Arsenal_V4' / 'webpanel' / 'frontend' / 'dashboard.html'
    dashboard_target = templates_dir / 'dashboard.html'
    
    try:
        if dashboard_target.exists():
            dashboard_target.unlink()
        dashboard_target.symlink_to(dashboard_source)
    except:
        # Si les liens symboliques ne fonctionnent pas, copier le fichier
        import shutil
        shutil.copy2(dashboard_source, dashboard_target)

# ==================== POINT D'ENTRÉE PRINCIPAL ====================

def main():
    """Point d'entrée principal"""
    print("🚀 Initialisation Arsenal V4 Ultimate...")
    
    # Vérifier les variables d'environnement
    discord_token = os.getenv('DISCORD_TOKEN')
    port = int(os.getenv('PORT', 10000))
    
    print(f"🔍 Configuration:")
    print(f"  - DISCORD_TOKEN: {'✅ Défini' if discord_token else '❌ Manquant'}")
    print(f"  - PORT: {port}")
    
    if not discord_token:
        print("❌ DISCORD_TOKEN manquant!")
        print("Ajoutez votre token Discord dans les variables d'environnement")
        sys.exit(1)
    
    # Créer les templates
    create_templates()
    
    # Démarrer la boucle de stats en arrière-plan
    threading.Thread(target=update_stats_loop, daemon=True).start()
    
    # Démarrer le bot automatiquement
    print("🤖 Démarrage automatique du bot...")
    start_discord_bot()
    
    # Démarrer le serveur Flask
    print(f"🌐 Démarrage du WebPanel sur le port {port}...")
    print("✅ Arsenal V4 Ultimate opérationnel!")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

if __name__ == "__main__":
    main()
