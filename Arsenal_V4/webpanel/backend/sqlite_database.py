#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import secrets
from datetime import datetime, timedelta
import json
import os

class ArsenalDatabase:
    def __init__(self):
        self.db_path = 'arsenal_v4.db'
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connexion à la base de données SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
            print("✅ Connexion SQLite réussie")
        except Exception as e:
            print(f"❌ Erreur SQLite: {e}")

    def create_tables(self):
        """Création des tables nécessaires"""
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    discriminator TEXT,
                    avatar TEXT,
                    access_level TEXT DEFAULT 'user',
                    is_banned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_commands INTEGER DEFAULT 0
                )
            """,
            
            'servers': """
                CREATE TABLE IF NOT EXISTS servers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner_id TEXT,
                    member_count INTEGER DEFAULT 0,
                    bot_joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    settings TEXT
                )
            """,
            
            'user_servers': """
                CREATE TABLE IF NOT EXISTS user_servers (
                    user_id TEXT,
                    server_id TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_member INTEGER DEFAULT 1,
                    PRIMARY KEY (user_id, server_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
                )
            """,
            
            'connected_servers': """
                CREATE TABLE IF NOT EXISTS connected_servers (
                    server_id TEXT PRIMARY KEY,
                    server_name TEXT NOT NULL,
                    member_count INTEGER DEFAULT 0,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'music_queue': """
                CREATE TABLE IF NOT EXISTS music_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id TEXT,
                    song_title TEXT,
                    song_url TEXT,
                    requested_by TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_playing BOOLEAN DEFAULT 0
                )
            """,
            
            'moderation_logs': """
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id TEXT,
                    moderator_id TEXT,
                    target_id TEXT,
                    action_type TEXT,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """,
            
            'bot_stats': """
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_servers INTEGER,
                    total_users INTEGER,
                    commands_executed INTEGER,
                    cpu_usage REAL,
                    memory_usage REAL,
                    uptime_seconds INTEGER,
                    discord_latency REAL
                )
            """,
            
            'commands_log': """
                CREATE TABLE IF NOT EXISTS commands_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    server_id TEXT,
                    command_name TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success INTEGER DEFAULT 1,
                    error_message TEXT
                )
            """,
            
            'panel_sessions': """
                CREATE TABLE IF NOT EXISTS panel_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_token TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """
        }

        try:
            cursor = self.connection.cursor()
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                print(f"✅ Table {table_name} créée/vérifiée")
            self.connection.commit()
        except Exception as e:
            print(f"❌ Erreur création tables: {e}")

    def add_user(self, user_id, username, discriminator=None, avatar=None):
        """Ajouter ou mettre à jour un utilisateur"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (id, username, discriminator, avatar, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, discriminator, avatar, datetime.now()))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur ajout utilisateur: {e}")
            return False

    def add_server(self, server_id, name, owner_id, member_count=0):
        """Ajouter ou mettre à jour un serveur"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO servers (id, name, owner_id, member_count)
                VALUES (?, ?, ?, ?)
            """, (server_id, name, owner_id, member_count))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur ajout serveur: {e}")
            return False

    def add_user_to_server(self, user_id, server_id):
        """Ajouter un utilisateur à un serveur"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_servers (user_id, server_id, is_member)
                VALUES (?, ?, 1)
            """, (user_id, server_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur ajout user/server: {e}")
            return False

    def user_has_access(self, user_id):
        """Vérifier si un utilisateur a accès au panel"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM user_servers us
                JOIN servers s ON us.server_id = s.id
                WHERE us.user_id = ? AND us.is_member = 1 AND s.is_active = 1
            """, (user_id,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"❌ Erreur vérification accès: {e}")
            return False

    def get_user_servers(self, user_id):
        """Obtenir les serveurs d'un utilisateur"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.id, s.name, s.member_count, us.joined_at
                FROM user_servers us
                JOIN servers s ON us.server_id = s.id
                WHERE us.user_id = ? AND us.is_member = 1 AND s.is_active = 1
                ORDER BY s.name
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur récupération serveurs: {e}")
            return []

    def get_stats(self):
        """Obtenir les statistiques générales"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Nombre total d'utilisateurs
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            # Nombre total de serveurs actifs
            cursor.execute("SELECT COUNT(*) FROM servers WHERE is_active = 1")
            stats['total_servers'] = cursor.fetchone()[0]
            
            # Nombre total de commandes exécutées
            cursor.execute("SELECT COUNT(*) FROM commands_log")
            stats['total_commands'] = cursor.fetchone()[0]
            
            # Commandes des dernières 24h
            cursor.execute("""
                SELECT COUNT(*) FROM commands_log 
                WHERE executed_at >= datetime('now', '-24 hours')
            """)
            stats['commands_24h'] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            print(f"❌ Erreur récupération stats: {e}")
            return {}

    def create_session(self, user_id, ip_address=None, user_agent=None):
        """Créer une session pour le panel"""
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO panel_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_token, expires_at, ip_address, user_agent))
            self.connection.commit()
            
            return session_token
        except Exception as e:
            print(f"❌ Erreur création session: {e}")
            return None

    def validate_session(self, session_token):
        """Valider une session"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.*, u.username, u.access_level
                FROM panel_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > datetime('now')
            """, (session_token,))
            
            result = cursor.fetchone()
            if result:
                session = dict(result)
                # Mettre à jour la dernière activité
                cursor.execute(
                    "UPDATE panel_sessions SET last_activity = datetime('now') WHERE session_token = ?",
                    (session_token,)
                )
                self.connection.commit()
                return session
            return None
        except Exception as e:
            print(f"❌ Erreur validation session: {e}")
            return None

    def get_recent_activity(self, limit=50):
        """Obtenir l'activité récente"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
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
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Erreur récupération activité: {e}")
            return []

    def log_command(self, user_id, server_id, command_name, parameters=None, success=True, execution_time=0.0):
        """Logger une commande exécutée"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO commands_log (user_id, server_id, command_name, parameters, success, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, server_id, command_name, parameters, success, execution_time))
            self.connection.commit()
            
            # Mettre à jour le compteur de commandes de l'utilisateur
            cursor.execute("UPDATE users SET total_commands = total_commands + 1 WHERE id = ?", (user_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur log commande: {e}")
            return False

    def populate_test_data(self):
        """Ajouter des données de test"""
        try:
            # Ajouter des utilisateurs de test
            test_users = [
                (123456789012345678, "XeRoX", "0001", None),
                (987654321098765432, "TestUser", "1234", None),
                (555666777888999000, "AdminUser", "9999", None)
            ]
            
            for user_data in test_users:
                self.add_user(*user_data)
            
            # Ajouter des serveurs de test
            test_servers = [
                (111222333444555666, "Arsenal Community", 123456789012345678, 250),
                (777888999000111222, "Gaming Hub", 987654321098765432, 1500),
                (333444555666777888, "Dev Server", 123456789012345678, 50)
            ]
            
            for server_data in test_servers:
                self.add_server(*server_data)
            
            # Lier les utilisateurs aux serveurs
            self.add_user_to_server(123456789012345678, 111222333444555666)
            self.add_user_to_server(123456789012345678, 777888999000111222)
            self.add_user_to_server(987654321098765432, 777888999000111222)
            
            print("✅ Données de test ajoutées")
            return True
        except Exception as e:
            print(f"❌ Erreur ajout données test: {e}")
            return False

    def close(self):
        """Fermer la connexion"""
        if self.connection:
            self.connection.close()
            print("🔒 Connexion SQLite fermée")
