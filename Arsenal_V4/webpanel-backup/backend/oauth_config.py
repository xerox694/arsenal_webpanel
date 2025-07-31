# Configuration OAuth Discord pour Arsenal V4 Webpanel
import os
import urllib.parse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Discord OAuth
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '1346646498040877076')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://arsenal-v4-webpanel.onrender.com/auth/callback')

# URLs Discord API
DISCORD_API_BASE = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = f'{DISCORD_API_BASE}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_BASE}/users/@me'
DISCORD_GUILDS_URL = f'{DISCORD_API_BASE}/users/@me/guilds'

# Scopes requis
DISCORD_SCOPES = ['identify', 'guilds']

class DiscordOAuth:
    """Classe pour gérer l'OAuth Discord"""
    
    def __init__(self):
        self.CLIENT_ID = DISCORD_CLIENT_ID
        self.CLIENT_SECRET = DISCORD_CLIENT_SECRET
        self.REDIRECT_URI = DISCORD_REDIRECT_URI
    
    def get_authorization_url(self, state=None):
        """Générer l'URL d'autorisation Discord"""
        params = f"client_id={self.CLIENT_ID}&redirect_uri={urllib.parse.quote(self.REDIRECT_URI)}&response_type=code&scope=identify+guilds"
        if state:
            params += f"&state={state}"
        return f"https://discord.com/api/oauth2/authorize?{params}"
    
    def get_token_url(self):
        """URL pour échanger le code contre un token"""
        return DISCORD_OAUTH_URL
    
    def get_user_info_url(self):
        """URL pour récupérer les infos utilisateur"""
        return DISCORD_USER_URL
    
    def get_user_guilds_url(self):
        """URL pour récupérer les serveurs de l'utilisateur"""
        return DISCORD_GUILDS_URL

def get_oauth_config():
    """Retourne la configuration OAuth"""
    return {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'api_base': DISCORD_API_BASE,
        'oauth_url': DISCORD_OAUTH_URL,
        'user_url': DISCORD_USER_URL,
        'guilds_url': DISCORD_GUILDS_URL,
        'scopes': DISCORD_SCOPES
    }

def validate_oauth_config():
    """Valide que la configuration OAuth est complète"""
    config = get_oauth_config()
    missing = []
    
    if not config['client_id'] or config['client_id'] == '':
        missing.append('DISCORD_CLIENT_ID')
    
    if not config['client_secret'] or config['client_secret'] == '':
        missing.append('DISCORD_CLIENT_SECRET')
    
    if not config['redirect_uri'] or config['redirect_uri'] == '':
        missing.append('DISCORD_REDIRECT_URI')
    
    return len(missing) == 0, missing
