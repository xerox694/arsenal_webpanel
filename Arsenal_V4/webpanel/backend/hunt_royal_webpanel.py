"""
🏹 HUNT ROYAL AUTH DATABASE - Arsenal Bot V4 (Webpanel Edition)
============================================================

Version adaptée pour le webpanel sans dépendances problématiques
"""

import sqlite3
import secrets
import json
from datetime import datetime, timedelta

class HuntRoyalAuthDatabase:
    """Gestionnaire de base de données pour l'authentification Hunt Royal (Webpanel)"""
    
    def __init__(self, db_path="hunt_royal_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données d'authentification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_royal_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                access_token TEXT UNIQUE NOT NULL,
                clan_role TEXT DEFAULT 'member',
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                permissions TEXT DEFAULT 'calculator_access'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_member(self, discord_id, username, clan_role='member'):
        """Enregistrer un nouveau membre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer un token unique
            access_token = secrets.token_urlsafe(32)
            
            cursor.execute('''
                INSERT OR REPLACE INTO hunt_royal_members 
                (discord_id, username, access_token, clan_role, registered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (discord_id, username, access_token, clan_role, datetime.now().isoformat()))
            
            conn.commit()
            return access_token
        except Exception as e:
            print(f"❌ Erreur enregistrement membre: {e}")
            return None
        finally:
            conn.close()
    
    def get_member_token(self, discord_id):
        """Récupérer le token d'un membre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT access_token, clan_role, is_active FROM hunt_royal_members WHERE discord_id = ?',
            (discord_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result and result[2]:  # is_active
            return {"token": result[0], "role": result[1]}
        return None
    
    def validate_token(self, token):
        """Valider un token d'accès"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT discord_id, username, clan_role, permissions 
            FROM hunt_royal_members 
            WHERE access_token = ? AND is_active = 1
        ''', (token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "discord_id": result[0],
                "username": result[1],
                "clan_role": result[2],
                "permissions": result[3].split(',') if result[3] else []
            }
        return None
    
    def log_access(self, discord_id, action, ip_address=None, user_agent=None):
        """Logger un accès"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_logs (discord_id, action, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (discord_id, action, ip_address, user_agent))
        
        conn.commit()
        conn.close()
    
    def regenerate_token(self, discord_id):
        """Régénérer le token d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer un nouveau token
            new_token = secrets.token_urlsafe(32)
            
            cursor.execute('''
                UPDATE hunt_royal_members 
                SET access_token = ?, last_login = ?
                WHERE discord_id = ? AND is_active = 1
            ''', (new_token, datetime.now().isoformat(), discord_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                self.log_access(discord_id, "token_regenerated")
                return new_token
            else:
                return None
        except Exception as e:
            print(f"❌ Erreur régénération token: {e}")
            return None
        finally:
            conn.close()

# Instance globale pour le webpanel
auth_db = HuntRoyalAuthDatabase()
