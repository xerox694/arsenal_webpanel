# 🚀 Arsenal V5 WebPanel - Serveur Principal
"""
Arsenal V5 WebPanel - Interface Web Moderne
Serveur Flask avec sidebar exceptionnelle et toutes les fonctionnalités du bot
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import sqlite3
from datetime import datetime, timedelta
import secrets
import hashlib
import asyncio
import threading
from functools import wraps
import time

# Configuration du serveur
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('WEBPANEL_SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CORS et SocketIO pour les interactions en temps réel
CORS(app, origins=["http://localhost:5000", "https://*.render.com"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration des paths
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
app.template_folder = TEMPLATE_DIR
app.static_folder = STATIC_DIR

print(f"🌐 [WebPanel V5] Template dir: {TEMPLATE_DIR}")
print(f"🌐 [WebPanel V5] Static dir: {STATIC_DIR}")

# Base de données pour les utilisateurs et sessions
DATABASE_PATH = 'webpanel_v5.db'

def init_database():
    """Initialise la base de données WebPanel"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table des utilisateurs autorisés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authorized_users (
            id INTEGER PRIMARY KEY,
            discord_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            permissions TEXT DEFAULT '{"all": true}'
        )
    ''')
    
    # Table des sessions actives
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY,
            session_id TEXT UNIQUE NOT NULL,
            discord_id TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # Table des logs d'activité
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY,
            discord_id TEXT,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ajouter l'utilisateur créateur par défaut
    creator_id = os.environ.get('CREATOR_ID', '431359112039890945')
    cursor.execute('''
        INSERT OR IGNORE INTO authorized_users (discord_id, username, role, permissions)
        VALUES (?, ?, ?, ?)
    ''', (creator_id, 'XeRoX (Creator)', 'creator', '{"all": true, "server_management": true, "user_management": true}'))
    
    conn.commit()
    conn.close()
    print("✅ [WebPanel V5] Base de données initialisée")

# Authentification et sécurité
def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Vérifier que la session est valide
        if not is_session_valid(session.get('session_id')):
            session.clear()
            flash('Session expirée, veuillez vous reconnecter.', 'warning')
            return redirect(url_for('login'))
        
        # Mettre à jour l'activité
        update_session_activity(session.get('session_id'))
        
        return f(*args, **kwargs)
    return decorated_function

def is_session_valid(session_id):
    """Vérifie si une session est valide"""
    if not session_id:
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT expires_at FROM active_sessions 
        WHERE session_id = ? AND expires_at > CURRENT_TIMESTAMP
    ''', (session_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_session_activity(session_id):
    """Met à jour l'activité de la session"""
    if not session_id:
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE active_sessions 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE session_id = ?
    ''', (session_id,))
    conn.commit()
    conn.close()

def log_activity(discord_id, action, details=None):
    """Enregistre une activité utilisateur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_logs (discord_id, action, details, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (discord_id, action, details, request.remote_addr if request else None))
    conn.commit()
    conn.close()

# Routes principales
@app.route('/')
def index():
    """Page d'accueil - redirige vers dashboard si connecté"""
    if 'user_id' in session and is_session_valid(session.get('session_id')):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Page de connexion"""
    return render_template('login.html')

@app.route('/dashboard')
@require_auth
def dashboard():
    """Dashboard principal avec sidebar"""
    user_info = get_user_info(session['user_id'])
    return render_template('dashboard.html', user=user_info)

# Pages du WebPanel avec sidebar
@app.route('/servers')
@require_auth
def servers_management():
    """Gestion des serveurs"""
    return render_template('servers.html', active_page='servers')

@app.route('/commands')
@require_auth
def commands_overview():
    """Vue d'ensemble des commandes"""
    return render_template('commands.html', active_page='commands')

@app.route('/music')
@require_auth
def music_system():
    """Système musical"""
    return render_template('music.html', active_page='music')

@app.route('/moderation')
@require_auth
def moderation_tools():
    """Outils de modération"""
    return render_template('moderation.html', active_page='moderation')

@app.route('/hunt-royal')
@require_auth
def hunt_royal():
    """Système Hunt Royal"""
    return render_template('hunt_royal.html', active_page='hunt-royal')

@app.route('/gaming')
@require_auth
def gaming_systems():
    """Systèmes de gaming"""
    return render_template('gaming.html', active_page='gaming')

@app.route('/social')
@require_auth
def social_features():
    """Fonctionnalités sociales"""
    return render_template('social.html', active_page='social')

@app.route('/crypto')
@require_auth
def crypto_integration():
    """Intégration crypto"""
    return render_template('crypto.html', active_page='crypto')

@app.route('/logs')
@require_auth
def system_logs():
    """Logs du système"""
    return render_template('logs.html', active_page='logs')

@app.route('/settings')
@require_auth
def settings():
    """Paramètres du WebPanel"""
    return render_template('settings.html', active_page='settings')

# API Routes pour les données en temps réel
@app.route('/api/bot/status')
@require_auth
def bot_status():
    """Status du bot en temps réel"""
    try:
        # Lire le fichier de status du bot
        if os.path.exists('../bot_status.json'):
            with open('../bot_status.json', 'r') as f:
                status = json.load(f)
        else:
            status = {
                "online": False,
                "status": "offline",
                "message": "Status non disponible"
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e), "online": False})

@app.route('/api/bot/servers')
@require_auth
def bot_servers():
    """Liste des serveurs du bot"""
    # Cette route sera connectée au bot Discord pour récupérer la liste des serveurs
    return jsonify({
        "servers": [],
        "total": 0,
        "message": "Intégration bot Discord en cours..."
    })

@app.route('/api/bot/commands/stats')
@require_auth
def commands_stats():
    """Statistiques d'utilisation des commandes"""
    return jsonify({
        "total_commands": 120,
        "most_used": [
            {"name": "/play", "uses": 1250},
            {"name": "/info", "uses": 890},
            {"name": "/hunt", "uses": 650}
        ],
        "recent_activity": []
    })

# Authentification Discord OAuth (simulée pour le moment)
@app.route('/auth/discord')
def discord_auth():
    """Authentification Discord OAuth"""
    # Pour le moment, connexion simulée avec le Creator ID
    creator_id = os.environ.get('CREATOR_ID', '431359112039890945')
    
    # Créer une session
    session_id = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Enregistrer la session
    cursor.execute('''
        INSERT INTO active_sessions (session_id, discord_id, ip_address, user_agent, expires_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, creator_id, request.remote_addr, request.headers.get('User-Agent'), expires_at))
    
    # Mettre à jour last_login
    cursor.execute('''
        UPDATE authorized_users SET last_login = CURRENT_TIMESTAMP WHERE discord_id = ?
    ''', (creator_id,))
    
    conn.commit()
    conn.close()
    
    # Créer la session Flask
    session['user_id'] = creator_id
    session['session_id'] = session_id
    session['username'] = 'XeRoX (Creator)'
    session.permanent = True
    
    log_activity(creator_id, 'login', 'Connexion WebPanel V5')
    
    flash('Connexion réussie ! Bienvenue sur Arsenal WebPanel V5 🚀', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Déconnexion"""
    if 'user_id' in session:
        log_activity(session['user_id'], 'logout', 'Déconnexion WebPanel V5')
    
    # Supprimer la session de la base
    if 'session_id' in session:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM active_sessions WHERE session_id = ?', (session['session_id'],))
        conn.commit()
        conn.close()
    
    session.clear()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('login'))

# Utilitaires
def get_user_info(discord_id):
    """Récupère les informations utilisateur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT discord_id, username, role, permissions, last_login
        FROM authorized_users WHERE discord_id = ?
    ''', (discord_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'discord_id': result[0],
            'username': result[1],
            'role': result[2],
            'permissions': json.loads(result[3] or '{}'),
            'last_login': result[4]
        }
    return None

# WebSocket pour les mises à jour en temps réel
@socketio.on('connect')
def handle_connect():
    """Gestion des connexions WebSocket"""
    if 'user_id' not in session:
        return False
    
    emit('connected', {'message': 'Connexion WebSocket établie'})
    print(f"🔗 [WebSocket] Utilisateur {session.get('username')} connecté")

@socketio.on('disconnect')
def handle_disconnect():
    """Gestion des déconnexions WebSocket"""
    print(f"🔌 [WebSocket] Utilisateur {session.get('username', 'Inconnu')} déconnecté")

# Nettoyage automatique des sessions expirées
def cleanup_expired_sessions():
    """Nettoie les sessions expirées"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM active_sessions WHERE expires_at < CURRENT_TIMESTAMP')
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"🧹 [Cleanup] {deleted} sessions expirées supprimées")

# Tâche de nettoyage automatique
def start_cleanup_task():
    """Démarre la tâche de nettoyage en arrière-plan"""
    def cleanup_loop():
        while True:
            time.sleep(3600)  # Nettoyage toutes les heures
            cleanup_expired_sessions()
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()

if __name__ == '__main__':
    print("🚀 [Arsenal WebPanel V5] Initialisation...")
    
    # Initialiser la base de données
    init_database()
    
    # Démarrer le nettoyage automatique
    start_cleanup_task()
    
    # Configuration du serveur
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 [WebPanel V5] Démarrage sur le port {port}")
    print(f"🔧 [WebPanel V5] Mode debug: {debug}")
    print(f"🎯 [WebPanel V5] URL: http://localhost:{port}")
    
    # Démarrer le serveur
    socketio.run(app, 
                host='0.0.0.0', 
                port=port, 
                debug=debug, 
                use_reloader=False)
