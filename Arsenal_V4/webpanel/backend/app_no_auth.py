#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal V4 WebPanel Backend - Version sans authentification
Backend Flask simplifié pour accès direct sans Discord OAuth
Auteur: xero3elite
Version: 4.3.1 - NO AUTH - TIMESTAMP: 2025-08-03_04:00
"""

from flask import Flask, request, jsonify, session, send_from_directory, redirect, make_response, send_file
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, join_room
import os
import sqlite3
import json
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import List

# ==================== CONFIGURATION ====================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# CORS Configuration
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, supports_credentials=True, origins=allowed_origins)

# SocketIO Configuration
socketio = SocketIO(app, cors_allowed_origins=allowed_origins)

print("🚀 Arsenal V4 WebPanel - Mode sans authentification activé")

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def index():
    """Accès direct au dashboard sans authentification"""
    print("🚀 ACCÈS DIRECT: Redirection vers dashboard sans authentification")
    return serve_dashboard_interface()

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - accès direct sans authentification"""
    print("🚀 DASHBOARD DIRECT: Accès sans authentification")
    return serve_dashboard_interface()

def serve_dashboard_interface():
    """Servir l'interface du dashboard pour les utilisateurs - Version sans auth"""
    try:
        # Chercher l'interface dans le dossier frontend
        frontend_paths = [
            # Version sans auth en premier
            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index_no_auth.html'),
            'Arsenal_V4/webpanel/frontend/index_no_auth.html',
            '/opt/render/project/src/Arsenal_V4/webpanel/frontend/index_no_auth.html',
            # Versions normales en fallback
            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html'),
            'Arsenal_V4/webpanel/frontend/index.html',
            '/opt/render/project/src/Arsenal_V4/webpanel/frontend/index.html'
        ]
        
        print(f"🔓 Recherche interface frontend SANS AUTH dans {len(frontend_paths)} emplacements...")
        
        for path in frontend_paths:
            try:
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"✅ INTERFACE TROUVÉE: {path} ({len(content)} chars)")
                    return content
            except Exception as e:
                print(f"❌ Erreur lecture {path}: {e}")
                continue
        
        print("⚠️ Aucune interface frontend trouvée, utilisation du fallback")
        
        # Interface de fallback simple
        return '''
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Arsenal V4 WebPanel - NO AUTH</title>
            <style>
                body { 
                    background: linear-gradient(120deg, #0a0a0f, #00fff7); 
                    color: white; 
                    font-family: Arial; 
                    text-align: center; 
                    padding: 50px; 
                }
                .success { 
                    font-size: 2em; 
                    color: #00ff88; 
                    animation: pulse 2s infinite; 
                }
                @keyframes pulse { 
                    0%, 100% { opacity: 1; } 
                    50% { opacity: 0.7; } 
                }
                .info {
                    margin: 20px 0;
                    padding: 20px;
                    background: rgba(0,255,247,0.1);
                    border-radius: 10px;
                    border: 1px solid #00fff7;
                }
            </style>
        </head>
        <body>
            <div class="success">🚀 Arsenal V4 WebPanel</div>
            <div class="info">
                <h2>✅ Mode Sans Authentification Activé</h2>
                <p>Backend fonctionnel - Accès direct sans Discord OAuth</p>
                <p>Version: 4.3.1 NO AUTH</p>
            </div>
            <div class="info">
                <h3>🔧 APIs Disponibles:</h3>
                <p>• <a href="/api/auth/user" style="color: #00fff7;">/api/auth/user</a> - Statut auth (bypass)</p>
                <p>• <a href="/api/stats" style="color: #00fff7;">/api/stats</a> - Statistiques bot</p>
                <p>• <a href="/api/bot/status" style="color: #00fff7;">/api/bot/status</a> - État du bot</p>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        print(f"❌ Erreur route dashboard: {e}")
        return f"Erreur dashboard: {str(e)}", 500

# ==================== ROUTES API AUTHENTIFICATION (BYPASS) ====================

@app.route('/api/auth/user')
def api_auth_user():
    """API - Toujours authentifié en mode bypass"""
    print("🔓 API AUTH BYPASS: Retour authentifié par défaut")
    return jsonify({
        'authenticated': True,
        'user': {
            'discord_id': 'bypass_user',
            'access_level': 'admin',
            'username': 'Admin Mode',
            'bypass_mode': True
        }
    })

# ==================== ROUTES API STATISTIQUES ====================

@app.route('/api/stats')
def get_stats():
    """Statistiques générales du bot"""
    return jsonify({
        'success': True,
        'stats': {
            'online': True,
            'servers': 42,
            'users': 1337,
            'commands_executed': 9999,
            'uptime': '24h 30m',
            'cpu_usage': '5%',
            'ram_usage': '120MB',
            'discord_latency': '25ms'
        }
    })

@app.route('/api/bot/status')
def bot_status():
    """Status du bot Discord"""
    return jsonify({
        'success': True,
        'status': {
            'online': True,
            'ping': '25ms',
            'servers': 42,
            'users': 1337,
            'uptime_hours': 24.5,
            'version': '4.3.1',
            'features': ['Music', 'Moderation', 'Economy', 'Games']
        }
    })

# ==================== ROUTES DE VERSION ====================

@app.route('/api/version')
def api_version():
    """Version de l'API"""
    return jsonify({
        'version': '4.3.1-no-auth',
        'mode': 'no_authentication',
        'timestamp': datetime.now().isoformat(),
        'backend': 'Flask',
        'authentication': 'disabled'
    })

# ==================== FICHIERS STATIQUES ====================

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Servir les fichiers JavaScript"""
    try:
        js_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'js'),
            'Arsenal_V4/webpanel/frontend/js',
            '/opt/render/project/src/Arsenal_V4/webpanel/frontend/js'
        ]
        
        for js_path in js_paths:
            if os.path.exists(js_path) and os.path.exists(os.path.join(js_path, filename)):
                return send_from_directory(js_path, filename, mimetype='application/javascript')
        
        return 'JS non trouvé', 404
    except Exception as e:
        return str(e), 500

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Servir les fichiers CSS"""
    try:
        css_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'frontend', 'css'),
            'Arsenal_V4/webpanel/frontend/css',
            '/opt/render/project/src/Arsenal_V4/webpanel/frontend/css'
        ]
        
        for css_path in css_paths:
            if os.path.exists(css_path) and os.path.exists(os.path.join(css_path, filename)):
                return send_from_directory(css_path, filename, mimetype='text/css')
        
        return 'CSS non trouvé', 404
    except Exception as e:
        return str(e), 500

# ==================== DÉMARRAGE ====================

if __name__ == '__main__':
    print("🚀 Arsenal V4 WebPanel - Mode NO AUTH")
    print("🔓 Authentification Discord désactivée")
    print("✅ Accès direct au dashboard autorisé")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    if os.environ.get('FLASK_ENV') == 'production':
        print(f"🌐 Production mode - Port: {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        print(f"🛠️ Development mode - Port: {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
