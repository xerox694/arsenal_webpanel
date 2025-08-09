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
- 🧠 AI Ultimate avec OpenAI + Gemini

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

# Initialiser AI Ultimate
try:
    from core.ai_ultimate import ai_ultimate
    print("🧠 AI Ultimate chargé avec succès")
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Ultimate non disponible: {e}")
    ai_ultimate = None
    AI_AVAILABLE = False

# Initialiser Gaming Ultimate (sans pygame)
try:
    from core.gaming_ultimate import gaming_ultimate
    print("🎮 Gaming Ultimate chargé avec succès (Mode Render)")
    GAMING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Gaming Ultimate non disponible: {e}")
    gaming_ultimate = None
    GAMING_AVAILABLE = False

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
    """Page d'accueil professionnelle"""
    return render_template('index_professional.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal professionnel"""
    return render_template('dashboard_professional.html')

@app.route('/login')
def login():
    """Page de connexion professionnelle"""
    return render_template('login_professional.html')

@app.route('/modules')
def modules():
    """Page des modules professionnelle"""
    return render_template('modules_professional.html')

# ==================== ROUTES FRONTEND ARSENAL V4 ====================

@app.route('/analytics')
def analytics():
    """Page Analytics"""
    return serve_frontend_page('analytics.html')

@app.route('/api')
def api_page():
    """Page API"""
    return serve_frontend_page('api.html')

@app.route('/automod')
def automod():
    """Page Auto-Modération"""
    return serve_frontend_page('automod.html')

@app.route('/backup')
def backup():
    """Page Backup"""
    return serve_frontend_page('backup.html')

@app.route('/botinfo')
def botinfo():
    """Page Info Bot"""
    return serve_frontend_page('botinfo.html')

@app.route('/bridges')
def bridges():
    """Page Ponts Inter-Serveur"""
    return serve_frontend_page('bridges.html')

@app.route('/calculator')
def calculator():
    """Page Calculator"""
    return serve_frontend_page('calculator.html')

@app.route('/commands')
def commands():
    """Page Commandes"""
    return serve_frontend_page('commands.html')

@app.route('/database')
def database():
    """Page Base de Données"""
    return serve_frontend_page('database.html')

@app.route('/economy')
def economy():
    """Page Économie"""
    return serve_frontend_page('economy.html')

@app.route('/economy-center')
def economy_center():
    """Page Economy Center"""
    return serve_frontend_page('economy-center.html')

@app.route('/economy-page')
def economy_page():
    """Page Economy Page"""
    return serve_frontend_page('economy-page.html')

@app.route('/games')
def games():
    """Page Mini-Jeux"""
    return serve_frontend_page('games.html')

@app.route('/games-ultimate')
def games_ultimate():
    """Page Games Ultimate"""
    return serve_frontend_page('games-ultimate.html')

@app.route('/help')
def help_page():
    """Page Help"""
    return serve_frontend_page('help.html')

@app.route('/hub')
def hub():
    """Page Hub Config"""
    return serve_frontend_page('hub.html')

@app.route('/logs')
def logs():
    """Page Logs"""
    return serve_frontend_page('logs.html')

@app.route('/moderation')
def moderation():
    """Page Modération"""
    return serve_frontend_page('moderation.html')

@app.route('/music')
def music():
    """Page Musique"""
    return serve_frontend_page('music.html')

@app.route('/music-center')
def music_center():
    """Page Music Center"""
    return serve_frontend_page('music-center.html')

@app.route('/performance')
def performance():
    """Page Performance"""
    return serve_frontend_page('performance.html')

@app.route('/realtime')
def realtime():
    """Page Temps Réel"""
    return serve_frontend_page('realtime.html')

@app.route('/security')
def security():
    """Page Sécurité"""
    return serve_frontend_page('security.html')

@app.route('/servers')
def servers():
    """Page Serveurs"""
    return serve_frontend_page('servers.html')

@app.route('/settings')
def settings():
    """Page Paramètres"""
    return serve_frontend_page('settings.html')

@app.route('/users')
def users():
    """Page Utilisateurs"""
    return serve_frontend_page('users.html')

@app.route('/ai-center')
def ai_center():
    """Page AI Center"""
    return serve_frontend_page('ai-center.html')

def serve_frontend_page(filename):
    """Fonction helper pour servir les pages du frontend"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), 'Arsenal_V4', 'webpanel', 'frontend')
        return send_from_directory(frontend_path, filename)
    except Exception as e:
        print(f"❌ Erreur lors du service de {filename}: {e}")
        return f"<h1>Page non trouvée</h1><p>Le fichier {filename} n'existe pas.</p>", 404

@app.route('/frontend/<path:filename>')
def serve_frontend_files(filename):
    """Servir les fichiers HTML du frontend"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), 'Arsenal_V4', 'webpanel', 'frontend')
        return send_from_directory(frontend_path, filename)
    except Exception as e:
        print(f"❌ Erreur lors du service du fichier {filename}: {e}")
        return jsonify({'error': f'Fichier non trouvé: {filename}'}), 404

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

@app.route('/api/test')
def test_api():
    """API - Test de connexion"""
    return jsonify({
        'status': 'ok',
        'message': 'Arsenal V4 API opérationnelle',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/servers/list')
def servers_list_api():
    """API - Liste des serveurs"""
    return jsonify({
        'success': True,
        'servers': [
            {
                'id': '123456789',
                'name': 'Serveur Test Arsenal',
                'members': 150,
                'online': 45,
                'icon': None
            }
        ]
    })

# ==================== AI ULTIMATE API ====================

@app.route('/api/ai/status')
def ai_status_api():
    """API - Statut AI Ultimate"""
    if not AI_AVAILABLE or not ai_ultimate:
        return jsonify({
            'available': False,
            'error': 'AI Ultimate non disponible'
        })
    
    return jsonify({
        'available': True,
        'providers': ai_ultimate.get_providers_status()
    })

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat_api():
    """API - Chat avec AI Ultimate"""
    if not AI_AVAILABLE or not ai_ultimate:
        return jsonify({
            'success': False,
            'error': 'AI Ultimate non disponible'
        })
    
    data = request.get_json()
    message = data.get('message', '')
    provider = data.get('provider')  # openai, gemini, ou None
    system_prompt = data.get('system_prompt')
    
    if not message:
        return jsonify({
            'success': False,
            'error': 'Message requis'
        })
    
    try:
        # Exécuter la requête AI en mode async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_ultimate.chat(message, provider, system_prompt)
        )
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur AI: {str(e)}'
        })

@app.route('/api/ai/translate', methods=['POST'])
def ai_translate_api():
    """API - Traduction avec AI Ultimate"""
    if not AI_AVAILABLE or not ai_ultimate:
        return jsonify({
            'success': False,
            'error': 'AI Ultimate non disponible'
        })
    
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('target', 'fr')
    provider = data.get('provider')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'Texte requis'
        })
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_ultimate.translate_text(text, target_language, provider)
        )
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur traduction: {str(e)}'
        })

@app.route('/api/ai/code', methods=['POST'])
def ai_code_api():
    """API - Génération de code avec AI Ultimate"""
    if not AI_AVAILABLE or not ai_ultimate:
        return jsonify({
            'success': False,
            'error': 'AI Ultimate non disponible'
        })
    
    data = request.get_json()
    description = data.get('description', '')
    language = data.get('language', 'python')
    provider = data.get('provider')
    
    if not description:
        return jsonify({
            'success': False,
            'error': 'Description requise'
        })
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_ultimate.generate_code(description, language, provider)
        )
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur génération code: {str(e)}'
        })

# ==================== GAMING ULTIMATE API ====================

@app.route('/api/gaming/status')
def gaming_status_api():
    """API - Statut Gaming Ultimate"""
    return jsonify({
        'available': GAMING_AVAILABLE,
        'mode': 'render_compatible',
        'games_available': ['coinflip', 'dice', 'roulette', 'blackjack', 'slots', 'quiz'] if GAMING_AVAILABLE else []
    })

@app.route('/api/gaming/play/<game_type>', methods=['POST'])
def play_game_api(game_type):
    """API - Jouer un jeu"""
    if not GAMING_AVAILABLE or not gaming_ultimate:
        return jsonify({
            'success': False,
            'error': 'Gaming Ultimate non disponible'
        })
    
    data = request.get_json() or {}
    user_id = data.get('user_id', 'anonymous')
    bet = data.get('bet', 50)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if game_type == 'coinflip':
            result = loop.run_until_complete(gaming_ultimate.coinflip(user_id, bet))
        elif game_type == 'dice':
            target = data.get('target', 6)
            result = loop.run_until_complete(gaming_ultimate.dice_roll(user_id, bet, target))
        elif game_type == 'roulette':
            choice = data.get('choice', 'rouge')
            result = loop.run_until_complete(gaming_ultimate.roulette(user_id, bet, choice))
        elif game_type == 'blackjack':
            result = loop.run_until_complete(gaming_ultimate.blackjack_simple(user_id, bet))
        elif game_type == 'slots':
            result = loop.run_until_complete(gaming_ultimate.slots_machine(user_id, bet))
        elif game_type == 'quiz':
            category = data.get('category', 'general')
            result = loop.run_until_complete(gaming_ultimate.quiz_question(user_id, category))
        elif game_type == 'number_guess':
            guess = data.get('guess', 50)
            result = loop.run_until_complete(gaming_ultimate.number_guessing(user_id, guess, bet))
        else:
            loop.close()
            return jsonify({
                'success': False,
                'error': f'Jeu {game_type} non reconnu'
            })
        
        # Mettre à jour les stats
        loop.run_until_complete(gaming_ultimate.update_user_stats(user_id, result))
        loop.close()
        
        return jsonify({
            'success': True,
            'game_result': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur jeu: {str(e)}'
        })

@app.route('/api/gaming/stats/<user_id>')
def gaming_stats_api(user_id):
    """API - Statistiques utilisateur"""
    if not GAMING_AVAILABLE or not gaming_ultimate:
        return jsonify({
            'success': False,
            'error': 'Gaming Ultimate non disponible'
        })
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stats = loop.run_until_complete(gaming_ultimate.get_user_stats(user_id))
        loop.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur stats: {str(e)}'
        })

@app.route('/api/gaming/leaderboard')
def gaming_leaderboard_api():
    """API - Classements Gaming"""
    if not GAMING_AVAILABLE or not gaming_ultimate:
        return jsonify({
            'success': False,
            'error': 'Gaming Ultimate non disponible'
        })
    
    category = request.args.get('category', 'winnings')
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        leaderboard = loop.run_until_complete(gaming_ultimate.get_leaderboard(category))
        loop.close()
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'category': category
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur leaderboard: {str(e)}'
        })

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
        
        # Chemin vers le bot (utiliser notre main.py corrigé)
        bot_dir = Path(__file__).parent
        bot_main = bot_dir / 'main.py'
        
        if not bot_main.exists():
            return False, f"❌ Fichier bot non trouvé: {bot_main}"
        
        # Environnement
        env = os.environ.copy()
        env['DISCORD_TOKEN'] = discord_token
        env['PYTHONPATH'] = str(bot_dir)
        
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
    
    # Note: dashboard.html existe déjà dans templates/, pas besoin de lien symbolique

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
