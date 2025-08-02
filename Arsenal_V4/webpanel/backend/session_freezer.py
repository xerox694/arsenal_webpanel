#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de Freeze pour les sessions OAuth Discord
Évite les changements de tokens pendant la connexion
"""

import time
import secrets
from datetime import datetime, timedelta
from threading import Lock

class SessionFreezer:
    def __init__(self):
        self.frozen_sessions = {}
        self.lock = Lock()
        
    def create_freeze(self, user_ip, user_agent):
        """Créer un freeze pour une session de connexion"""
        freeze_token = secrets.token_urlsafe(32)
        
        with self.lock:
            self.frozen_sessions[freeze_token] = {
                'created_at': datetime.now(),
                'user_ip': user_ip,
                'user_agent': user_agent,
                'oauth_tokens': {},
                'discord_data': None,
                'status': 'freezing',
                'expires_at': datetime.now() + timedelta(minutes=10)  # Expire après 10 min
            }
        
        print(f"🧊 FREEZE CRÉÉ: {freeze_token} pour IP {user_ip}")
        return freeze_token
    
    def add_oauth_token(self, freeze_token, access_token, refresh_token=None):
        """Ajouter les tokens OAuth au freeze"""
        with self.lock:
            if freeze_token in self.frozen_sessions:
                self.frozen_sessions[freeze_token]['oauth_tokens'] = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'frozen_at': datetime.now()
                }
                self.frozen_sessions[freeze_token]['status'] = 'tokens_frozen'
                print(f"🔐 TOKENS FIGÉS: {freeze_token}")
                return True
            return False
    
    def add_discord_data(self, freeze_token, user_data, guilds_data):
        """Ajouter les données Discord au freeze"""
        with self.lock:
            if freeze_token in self.frozen_sessions:
                self.frozen_sessions[freeze_token]['discord_data'] = {
                    'user': user_data,
                    'guilds': guilds_data,
                    'retrieved_at': datetime.now()
                }
                self.frozen_sessions[freeze_token]['status'] = 'data_complete'
                print(f"👤 DONNÉES DISCORD FIGÉES: {freeze_token}")
                return True
            return False
    
    def get_frozen_session(self, freeze_token):
        """Récupérer une session figée"""
        with self.lock:
            session = self.frozen_sessions.get(freeze_token)
            if session and session['expires_at'] > datetime.now():
                return session
            elif session:
                # Session expirée, la supprimer
                del self.frozen_sessions[freeze_token]
                print(f"⏰ SESSION EXPIRÉE: {freeze_token}")
            return None
    
    def unfreeze_session(self, freeze_token):
        """Libérer une session figée après connexion réussie"""
        with self.lock:
            if freeze_token in self.frozen_sessions:
                session_data = self.frozen_sessions[freeze_token]
                del self.frozen_sessions[freeze_token]
                print(f"🔓 SESSION LIBÉRÉE: {freeze_token}")
                return session_data
            return None
    
    def cleanup_expired(self):
        """Nettoyer les sessions expirées"""
        now = datetime.now()
        expired_tokens = []
        
        with self.lock:
            for token, session in self.frozen_sessions.items():
                if session['expires_at'] <= now:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.frozen_sessions[token]
                print(f"🗑️ SESSION EXPIRÉE SUPPRIMÉE: {token}")
        
        return len(expired_tokens)

# Instance globale du freezer
session_freezer = SessionFreezer()

def create_login_freeze(request):
    """Créer un freeze pour une nouvelle connexion"""
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    return session_freezer.create_freeze(user_ip, user_agent)

def freeze_oauth_tokens(freeze_token, access_token, refresh_token=None):
    """Figer les tokens OAuth"""
    return session_freezer.add_oauth_token(freeze_token, access_token, refresh_token)

def freeze_discord_data(freeze_token, user_data, guilds_data):
    """Figer les données Discord"""
    return session_freezer.add_discord_data(freeze_token, user_data, guilds_data)

def get_frozen_data(freeze_token):
    """Récupérer les données figées"""
    return session_freezer.get_frozen_session(freeze_token)

def complete_login_freeze(freeze_token):
    """Terminer le freeze et retourner les données"""
    return session_freezer.unfreeze_session(freeze_token)
