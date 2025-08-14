#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class ArsenalDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connexion à la base de données MySQL"""
        try:
            # SÉCURITÉ: Utiliser des variables d'environnement pour les credentials
            import os
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'arsenal_v4'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),  # IMPORTANT: Configurer DB_PASSWORD dans .env
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            print("✅ Connexion MySQL réussie")
        except Error as e:
            print(f"❌ Erreur MySQL: {e}")
            # Fallback: créer la base si elle n'existe pas
            try:
                import os
                self.connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    user=os.getenv('DB_USER', 'root'),
                    password=os.getenv('DB_PASSWORD', '')  # IMPORTANT: Configurer DB_PASSWORD dans .env
                )
                cursor = self.connection.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS arsenal_v4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.execute("USE arsenal_v4")
                print("✅ Base de données Arsenal_V4 créée")
            except Error as e2:
                print(f"❌ Impossible de créer la base: {e2}")

    def create_tables(self):
        """Création des tables nécessaires"""
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    discriminator VARCHAR(10),
                    avatar VARCHAR(255),
                    access_level ENUM('user', 'moderator', 'admin', 'owner') DEFAULT 'user',
                    is_banned BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_commands INT DEFAULT 0,
                    INDEX idx_username (username),
                    INDEX idx_access_level (access_level)
                )
            """,
            
            'servers': """
                CREATE TABLE IF NOT EXISTS servers (
                    id BIGINT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    owner_id BIGINT,
                    member_count INT DEFAULT 0,
                    bot_joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    settings JSON,
                    INDEX idx_owner (owner_id),
                    INDEX idx_active (is_active)
                )
            """,
            
            'user_servers': """
                CREATE TABLE IF NOT EXISTS user_servers (
                    user_id BIGINT,
                    server_id BIGINT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_member BOOLEAN DEFAULT TRUE,
                    PRIMARY KEY (user_id, server_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
                )
            """,
            
            'commands_log': """
                CREATE TABLE IF NOT EXISTS commands_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    server_id BIGINT,
                    command_name VARCHAR(100),
                    parameters TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE,
                    execution_time FLOAT,
                    INDEX idx_user_id (user_id),
                    INDEX idx_server_id (server_id),
                    INDEX idx_command (command_name),
                    INDEX idx_executed_at (executed_at)
                )
            """,
            
            'bot_stats': """
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_servers INT,
                    total_users INT,
                    commands_executed INT,
                    cpu_usage FLOAT,
                    memory_usage FLOAT,
                    uptime_seconds INT,
                    discord_latency FLOAT,
                    INDEX idx_timestamp (timestamp)
                )
            """,
            
            'access_tokens': """
                CREATE TABLE IF NOT EXISTS access_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    token VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_token (token),
                    INDEX idx_user_id (user_id),
                    INDEX idx_expires (expires_at)
                )
            """,
            
            'panel_sessions': """
                CREATE TABLE IF NOT EXISTS panel_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    session_token VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_token (session_token),
                    INDEX idx_user_id (user_id),
                    INDEX idx_active (is_active)
                )
            """
        }

        try:
            cursor = self.connection.cursor()
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                print(f"✅ Table {table_name} créée/vérifiée")
            self.connection.commit()
        except Error as e:
            print(f"❌ Erreur création tables: {e}")

    def add_user(self, user_id, username, discriminator=None, avatar=None):
        """Ajouter ou mettre à jour un utilisateur"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO users (id, username, discriminator, avatar, last_seen)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                username = VALUES(username),
                discriminator = VALUES(discriminator),
                avatar = VALUES(avatar),
                last_seen = VALUES(last_seen)
            """
            cursor.execute(query, (user_id, username, discriminator, avatar, datetime.now()))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ Erreur ajout utilisateur: {e}")
            return False

    def add_server(self, server_id, name, owner_id, member_count=0):
        """Ajouter ou mettre à jour un serveur"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO servers (id, name, owner_id, member_count)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                owner_id = VALUES(owner_id),
                member_count = VALUES(member_count)
            """
            cursor.execute(query, (server_id, name, owner_id, member_count))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ Erreur ajout serveur: {e}")
            return False

    def user_has_access(self, user_id):
        """Vérifier si un utilisateur a accès au panel"""
        try:
            cursor = self.connection.cursor()
            
            # Vérifier si l'utilisateur est dans au moins un serveur avec le bot
            query = """
                SELECT COUNT(*) FROM user_servers us
                JOIN servers s ON us.server_id = s.id
                WHERE us.user_id = %s AND us.is_member = TRUE AND s.is_active = TRUE
            """
            cursor.execute(query, (user_id,))
            count = cursor.fetchone()[0]
            
            return count > 0
        except Error as e:
            print(f"❌ Erreur vérification accès: {e}")
            return False

    def get_user_servers(self, user_id):
        """Obtenir les serveurs d'un utilisateur"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT s.id, s.name, s.member_count, us.joined_at
                FROM user_servers us
                JOIN servers s ON us.server_id = s.id
                WHERE us.user_id = %s AND us.is_member = TRUE AND s.is_active = TRUE
                ORDER BY s.name
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Erreur récupération serveurs: {e}")
            return []

    def log_command(self, user_id, server_id, command_name, parameters=None, success=True, execution_time=0.0):
        """Logger une commande exécutée"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO commands_log (user_id, server_id, command_name, parameters, success, execution_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, server_id, command_name, parameters, success, execution_time))
            self.connection.commit()
            
            # Mettre à jour le compteur de commandes de l'utilisateur
            cursor.execute("UPDATE users SET total_commands = total_commands + 1 WHERE id = %s", (user_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ Erreur log commande: {e}")
            return False

    def get_stats(self):
        """Obtenir les statistiques générales"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            stats = {}
            
            # Nombre total d'utilisateurs
            cursor.execute("SELECT COUNT(*) as total FROM users")
            stats['total_users'] = cursor.fetchone()['total']
            
            # Nombre total de serveurs actifs
            cursor.execute("SELECT COUNT(*) as total FROM servers WHERE is_active = TRUE")
            stats['total_servers'] = cursor.fetchone()['total']
            
            # Nombre total de commandes exécutées
            cursor.execute("SELECT COUNT(*) as total FROM commands_log")
            stats['total_commands'] = cursor.fetchone()['total']
            
            # Commandes des dernières 24h
            cursor.execute("""
                SELECT COUNT(*) as total FROM commands_log 
                WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)
            stats['commands_24h'] = cursor.fetchone()['total']
            
            # Utilisateurs actifs (dernière semaine)
            cursor.execute("""
                SELECT COUNT(*) as total FROM users 
                WHERE last_seen >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            stats['active_users'] = cursor.fetchone()['total']
            
            return stats
        except Error as e:
            print(f"❌ Erreur récupération stats: {e}")
            return {}

    def create_session(self, user_id, ip_address=None, user_agent=None):
        """Créer une session pour le panel"""
        try:
            # Générer un token sécurisé
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)  # 24h d'expiration
            
            cursor = self.connection.cursor()
            query = """
                INSERT INTO panel_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, session_token, expires_at, ip_address, user_agent))
            self.connection.commit()
            
            return session_token
        except Error as e:
            print(f"❌ Erreur création session: {e}")
            return None

    def validate_session(self, session_token):
        """Valider une session"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT s.*, u.username, u.access_level
                FROM panel_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.is_active = TRUE AND s.expires_at > NOW()
            """
            cursor.execute(query, (session_token,))
            session = cursor.fetchone()
            
            if session:
                # Mettre à jour la dernière activité
                cursor.execute(
                    "UPDATE panel_sessions SET last_activity = NOW() WHERE session_token = %s",
                    (session_token,)
                )
                self.connection.commit()
                
            return session
        except Error as e:
            print(f"❌ Erreur validation session: {e}")
            return None

    def get_recent_activity(self, limit=50):
        """Obtenir l'activité récente"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    c.command_name,
                    c.executed_at,
                    c.success,
                    u.username,
                    s.name as server_name
                FROM commands_log c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN servers s ON c.server_id = s.id
                ORDER BY c.executed_at DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Erreur récupération activité: {e}")
            return []

    def close(self):
        """Fermer la connexion"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Connexion MySQL fermée")
