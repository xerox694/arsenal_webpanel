"""
🏹 HUNT ROYAL AUTH DATABASE - Arsenal Bot V4 (Ultra-Advanced Edition)
====================================================================

Système d'authentification avancé avec codes courts et sessions sécurisées
"""

import sqlite3
import secrets
import hashlib
import json
from datetime import datetime, timedelta

class HuntRoyalAuthDatabase:
    """Gestionnaire ultra-avancé pour l'authentification Hunt Royal"""
    
    def __init__(self, db_path="hunt_royal_auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données avec toutes les tables avancées"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale des membres (compatible avec Discord bot)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_royal_members (
                discord_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                display_name TEXT,
                access_token TEXT UNIQUE NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                clan_role TEXT DEFAULT 'Member',
                permissions TEXT DEFAULT 'calculator_access',
                game_id_new TEXT,
                game_id_old TEXT,
                clan_name TEXT,
                notes TEXT,
                registered_at TEXT NOT NULL,
                last_login TEXT,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Logs d'accès enrichis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT,
                username TEXT,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN DEFAULT 1,
                details TEXT,
                login_method TEXT DEFAULT 'token',
                FOREIGN KEY (discord_id) REFERENCES hunt_royal_members (discord_id)
            )
        ''')
        
        # Sessions sécurisées pour le webpanel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_sessions (
                session_id TEXT PRIMARY KEY,
                discord_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (discord_id) REFERENCES hunt_royal_members (discord_id)
            )
        ''')
        
        # Hiérarchie des clans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_hierarchy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_name TEXT NOT NULL,
                discord_id TEXT NOT NULL,
                appointed_role TEXT NOT NULL,
                appointed_by TEXT,
                appointed_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (discord_id) REFERENCES hunt_royal_members (discord_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def validate_token(self, token):
        """Valider un token d'accès complet (32 caractères)"""
        return self._validate_credential(token, "access_token")
    
    def validate_short_code(self, short_code, username_hint=None):
        """Valider un code court (7-10 chiffres) avec indice de nom"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recherche avec indice de nom si fourni
        if username_hint:
            cursor.execute('''
                SELECT discord_id, username, display_name, clan_role, permissions,
                       access_token, short_code, game_id_new, game_id_old, clan_name, login_count
                FROM hunt_royal_members 
                WHERE short_code = ? AND 
                      (username LIKE ? OR display_name LIKE ?) AND 
                      is_active = 1
            ''', (short_code, f"%{username_hint}%", f"%{username_hint}%"))
        else:
            # Recherche uniquement par code
            cursor.execute('''
                SELECT discord_id, username, display_name, clan_role, permissions,
                       access_token, short_code, game_id_new, game_id_old, clan_name, login_count
                FROM hunt_royal_members 
                WHERE short_code = ? AND is_active = 1
            ''', (short_code,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Logger l'accès réussi
            self._log_access(result[0], "webpanel_shortcode_login", success=True, 
                           details=f"Code: {short_code}, Hint: {username_hint}")
            
            # Incrémenter le compteur
            self._increment_login_count(result[0])
            
            return {
                "valid": True,
                "discord_id": result[0],
                "username": result[1],
                "display_name": result[2] or result[1],
                "clan_role": result[3],
                "permissions": result[4].split(',') if result[4] else [],
                "tokens": {"full": result[5], "short": result[6]},
                "game_ids": {"new": result[7], "old": result[8]},
                "clan_name": result[9],
                "login_count": result[10] + 1,
                "login_method": "short_code"
            }
        
        # Logger l'échec
        self._log_access(None, "webpanel_shortcode_login", success=False,
                        details=f"Failed code: {short_code}, Hint: {username_hint}")
        return {"valid": False, "error": "Code court invalide ou utilisateur introuvable"}
    
    def alternative_login(self, identifier, username_hint=None):
        """Méthode de connexion alternative (token OU code court)"""
        # Essayer d'abord comme token complet
        if len(identifier) > 15:  # Probablement un token
            return self.validate_token(identifier)
        
        # Sinon, traiter comme code court
        return self.validate_short_code(identifier, username_hint)
    
    def _validate_credential(self, credential, field_name):
        """Validation générique d'un identifiant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT discord_id, username, display_name, clan_role, permissions,
                   access_token, short_code, game_id_new, game_id_old, clan_name, login_count
            FROM hunt_royal_members 
            WHERE {field_name} = ? AND is_active = 1
        ''', (credential,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Logger l'accès réussi
            self._log_access(result[0], f"webpanel_{field_name}_login", success=True)
            
            # Incrémenter le compteur de connexions
            self._increment_login_count(result[0])
            
            return {
                "valid": True,
                "discord_id": result[0],
                "username": result[1],
                "display_name": result[2] or result[1],
                "clan_role": result[3],
                "permissions": result[4].split(',') if result[4] else [],
                "tokens": {"full": result[5], "short": result[6]},
                "game_ids": {"new": result[7], "old": result[8]},
                "clan_name": result[9],
                "login_count": result[10] + 1,
                "login_method": "token" if field_name == "access_token" else "short_code"
            }
        
        # Logger l'échec
        self._log_access(None, f"webpanel_{field_name}_login", success=False, 
                        details=f"Failed credential: {credential[:8]}...")
        return {"valid": False, "error": "Identifiants invalides"}
    
    def admin_bypass_login(self, creator_token=None):
        """Bypass de connexion pour le créateur du bot"""
        # Token spécial créateur (à configurer)
        CREATOR_TOKENS = [
            "XEROX694_CREATOR_ACCESS",  # Token spécial créateur
            "ARSENAL_BOT_FOUNDER",      # Token fondateur
            "ADMIN_BYPASS_2025"         # Token admin bypass
        ]
        
        if creator_token in CREATOR_TOKENS:
            return {
                "valid": True,
                "discord_id": "CREATOR_XEROX694",
                "username": "xerox694",
                "display_name": "🔰 CRÉATEUR ARSENAL BOT",
                "clan_role": "FOUNDER",
                "permissions": ["ALL_ACCESS", "ADMIN", "FOUNDER", "BYPASS"],
                "tokens": {"full": creator_token, "short": "0000000"},
                "game_ids": {"new": "CREATOR", "old": "FOUNDER"},
                "clan_name": "🏹 ARSENAL TEAM",
                "login_count": 999,
                "login_method": "creator_bypass",
                "bypass": True
            }
        
        return {"valid": False, "error": "Token créateur invalide"}
    
    def get_creator_dashboard(self):
        """Dashboard spécial pour le créateur"""
        return {
            "found": True,
            "user_info": {
                "username": "xerox694",
                "display_name": "🔰 CRÉATEUR ARSENAL BOT",
                "clan_role": "FOUNDER",
                "permissions": ["ALL_ACCESS", "ADMIN", "FOUNDER", "BYPASS"],
                "game_ids": {"new": "CREATOR", "old": "FOUNDER"},
                "clan_name": "🏹 ARSENAL TEAM",
                "notes": "Créateur et fondateur d'Arsenal Bot",
                "registered_at": "2024-01-01T00:00:00",
                "last_login": "NOW",
                "login_count": 999
            },
            "tokens": {
                "full_token": "XEROX694_CREATOR_ACCESS",
                "short_code": "0000000",
                "can_copy": True,
                "can_regenerate": True
            },
            "statistics": {
                "total_access": 9999,
                "successful_access": 9999,
                "failed_access": 0,
                "calculator_usage": 999,
                "webpanel_usage": 999,
                "success_rate": 100.0
            },
            "sessions": {
                "active_count": 1,
                "next_expiry": "NEVER"
            },
            "recent_activity": [
                {
                    "action": "creator_access",
                    "timestamp": "NOW",
                    "success": True,
                    "details": "Accès créateur",
                    "method": "bypass",
                    "ip": "CREATOR"
                }
            ],
            "creator_features": {
                "can_access_all_users": True,
                "can_modify_any_data": True,
                "can_see_all_logs": True,
                "bypass_all_restrictions": True
            }
        }
    
    def create_security_session(self, discord_id, ip_address=None, user_agent=None):
        """Créer une session sécurisée pour maintenir la connexion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer un ID de session unique
            session_id = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(f"{discord_id}_{session_id}".encode()).hexdigest()
            
            # Session valide 24h par défaut
            created_at = datetime.now()
            expires_at = datetime.fromtimestamp(created_at.timestamp() + 86400)  # +24h
            
            cursor.execute('''
                INSERT INTO security_sessions 
                (session_id, discord_id, token_hash, created_at, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, discord_id, token_hash, 
                  created_at.isoformat(), expires_at.isoformat(), 
                  ip_address, user_agent))
            
            conn.commit()
            self._log_access(discord_id, "session_created", success=True, 
                           details=f"Session: {session_id[:12]}..., IP: {ip_address}")
            
            return {
                "success": True,
                "session_id": session_id,
                "expires_at": expires_at.isoformat(),
                "valid_for_hours": 24
            }
            
        except Exception as e:
            print(f"❌ Erreur création session: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def validate_session(self, session_id):
        """Valider une session existante et récupérer les infos utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.discord_id, s.expires_at, m.username, m.display_name, 
                   m.clan_role, m.permissions, m.clan_name
            FROM security_sessions s
            JOIN hunt_royal_members m ON s.discord_id = m.discord_id
            WHERE s.session_id = ? AND s.is_active = 1 AND m.is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            expires_at = datetime.fromisoformat(result[1])
            if datetime.now() < expires_at:
                # Session toujours valide
                self._log_access(result[0], "session_validated", success=True)
                return {
                    "valid": True,
                    "discord_id": result[0],
                    "username": result[2],
                    "display_name": result[3] or result[2],
                    "clan_role": result[4],
                    "permissions": result[5].split(',') if result[5] else [],
                    "clan_name": result[6],
                    "expires_at": result[1]
                }
            else:
                # Session expirée
                self._deactivate_session(session_id)
                self._log_access(result[0], "session_expired", success=False)
        
        return {"valid": False, "error": "Session invalide ou expirée"}
    
    def regenerate_user_tokens(self, discord_id):
        """Régénérer les tokens complet et court d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Générer nouveaux tokens
            new_token = secrets.token_urlsafe(32)
            new_short_code = ''.join([str(secrets.randbelow(10)) for _ in range(secrets.randbelow(4) + 7)])
            
            cursor.execute('''
                UPDATE hunt_royal_members 
                SET access_token = ?, short_code = ?, last_login = ?
                WHERE discord_id = ? AND is_active = 1
            ''', (new_token, new_short_code, datetime.now().isoformat(), discord_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                self._log_access(discord_id, "tokens_regenerated", success=True,
                              details=f"New short code: {new_short_code}")
                return {
                    "success": True,
                    "new_token": new_token,
                    "new_short_code": new_short_code,
                    "regenerated_at": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Utilisateur non trouvé"}
                
        except Exception as e:
            print(f"❌ Erreur régénération tokens: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def get_user_dashboard_data(self, discord_id):
        """Récupérer toutes les données pour le dashboard utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Infos utilisateur complètes
        cursor.execute('''
            SELECT username, display_name, clan_role, permissions, game_id_new, game_id_old,
                   clan_name, notes, registered_at, last_login, login_count, access_token, short_code
            FROM hunt_royal_members 
            WHERE discord_id = ? AND is_active = 1
        ''', (discord_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return {"found": False, "error": "Utilisateur non trouvé"}
        
        # Statistiques d'accès détaillées
        cursor.execute('''
            SELECT COUNT(*) as total_access,
                   COUNT(CASE WHEN success = 1 THEN 1 END) as successful_access,
                   COUNT(CASE WHEN success = 0 THEN 1 END) as failed_access,
                   MAX(timestamp) as last_access,
                   COUNT(CASE WHEN action LIKE '%calculator%' THEN 1 END) as calculator_usage,
                   COUNT(CASE WHEN action LIKE '%webpanel%' THEN 1 END) as webpanel_usage
            FROM access_logs 
            WHERE discord_id = ?
        ''', (discord_id,))
        
        stats = cursor.fetchone()
        
        # Sessions actives
        cursor.execute('''
            SELECT COUNT(*) as active_sessions, 
                   MIN(expires_at) as next_expiry
            FROM security_sessions 
            WHERE discord_id = ? AND is_active = 1 AND expires_at > ?
        ''', (discord_id, datetime.now().isoformat()))
        
        session_info = cursor.fetchone()
        
        # Historique récent (10 dernières actions)
        cursor.execute('''
            SELECT action, timestamp, success, details, login_method, ip_address
            FROM access_logs 
            WHERE discord_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (discord_id,))
        
        recent_activity = cursor.fetchall()
        conn.close()
        
        return {
            "found": True,
            "user_info": {
                "username": user_data[0],
                "display_name": user_data[1] or user_data[0],
                "clan_role": user_data[2],
                "permissions": user_data[3].split(',') if user_data[3] else [],
                "game_ids": {"new": user_data[4], "old": user_data[5]},
                "clan_name": user_data[6],
                "notes": user_data[7],
                "registered_at": user_data[8],
                "last_login": user_data[9],
                "login_count": user_data[10]
            },
            "tokens": {
                "full_token": user_data[11],
                "short_code": user_data[12],
                "can_copy": True,
                "can_regenerate": True
            },
            "statistics": {
                "total_access": stats[0] or 0,
                "successful_access": stats[1] or 0,
                "failed_access": stats[2] or 0,
                "last_access": stats[3],
                "calculator_usage": stats[4] or 0,
                "webpanel_usage": stats[5] or 0,
                "success_rate": round((stats[1] / stats[0] * 100) if stats[0] > 0 else 100, 1)
            },
            "sessions": {
                "active_count": session_info[0] or 0,
                "next_expiry": session_info[1]
            },
            "recent_activity": [
                {
                    "action": activity[0],
                    "timestamp": activity[1],
                    "success": bool(activity[2]),
                    "details": activity[3],
                    "method": activity[4],
                    "ip": activity[5]
                } for activity in recent_activity
            ]
        }
    
    def _increment_login_count(self, discord_id):
        """Incrémenter le compteur de connexions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE hunt_royal_members 
            SET login_count = login_count + 1, last_login = ?
            WHERE discord_id = ?
        ''', (datetime.now().isoformat(), discord_id))
        conn.commit()
        conn.close()
    
    def _log_access(self, discord_id, action, ip_address=None, user_agent=None, success=True, details=None):
        """Logger un accès dans la base avec toutes les informations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer le username si disponible
        username = None
        if discord_id:
            cursor.execute('SELECT username FROM hunt_royal_members WHERE discord_id = ?', (discord_id,))
            result = cursor.fetchone()
            username = result[0] if result else None
        
        cursor.execute('''
            INSERT INTO access_logs 
            (discord_id, username, action, timestamp, ip_address, user_agent, success, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (discord_id, username, action, datetime.now().isoformat(), 
              ip_address, user_agent, success, details))
        
        conn.commit()
        conn.close()
    
    def _deactivate_session(self, session_id):
        """Désactiver une session expirée ou révoquée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE security_sessions SET is_active = 0 WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def logout_user(self, discord_id):
        """Déconnecter un utilisateur (désactiver toutes ses sessions)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE security_sessions SET is_active = 0 WHERE discord_id = ?', (discord_id,))
        deactivated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        self._log_access(discord_id, "user_logout", success=True, 
                        details=f"Désactivé {deactivated_count} sessions")
        
        return {"success": True, "sessions_deactivated": deactivated_count}

# Instance globale pour l'import  
hunt_royal_auth_db = HuntRoyalAuthDatabase()

# Alias pour compatibilité
auth_db = hunt_royal_auth_db
