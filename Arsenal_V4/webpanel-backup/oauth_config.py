#!/usr/bin/env python3
"""
Configuration OAuth Discord pour Arsenal_V4 WebPanel
"""
import os
import urllib.parse

class DiscordOAuth:
    def __init__(self):
        # Configuration à partir des variables d'environnement
        self.CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID', '1346646498040877076')
        self.CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET', '')
        self.REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI', 'https://arsenal-v4-webpanel.onrender.com/auth/callback')
        self.BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')
        
        # URLs Discord
        self.DISCORD_API_BASE = 'https://discord.com/api/v10'
        self.DISCORD_OAUTH_BASE = 'https://discord.com/api/oauth2'
        
    def get_authorization_url(self, state=None):
        """Générer l'URL d'autorisation Discord"""
        params = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'identify guilds',
        }
        
        if state:
            params['state'] = state
            
        return f"{self.DISCORD_OAUTH_BASE}/authorize?" + urllib.parse.urlencode(params)
    
    def get_token_url(self):
        """URL pour échanger le code contre un token"""
        return f"{self.DISCORD_OAUTH_BASE}/token"
    
    def get_user_info_url(self):
        """URL pour récupérer les infos utilisateur"""
        return f"{self.DISCORD_API_BASE}/users/@me"
    
    def get_user_guilds_url(self):
        """URL pour récupérer les serveurs de l'utilisateur"""
        return f"{self.DISCORD_API_BASE}/users/@me/guilds"
