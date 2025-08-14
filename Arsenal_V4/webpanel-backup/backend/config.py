import os
from datetime import timedelta
import secrets

class Config:
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Configuration Discord OAuth
    DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID') or 'YOUR_DISCORD_CLIENT_ID'
    DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET') or 'YOUR_DISCORD_CLIENT_SECRET'
    DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI') or 'http://localhost:5000/auth/callback'
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN') or 'YOUR_BOT_TOKEN'
    
    # Configuration Base de données
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///arsenal_v4.db'
    
    # Configuration Redis (pour le cache)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Configuration Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration CORS
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5000',
        # Ajouter votre domaine en production
    ]
    
    # Configuration WebPanel
    WEBPANEL_URL = os.environ.get('WEBPANEL_URL') or 'http://localhost:5000'
    
    # Configuration API
    API_RATE_LIMIT = '1000 per hour'  # Rate limiting
    
    # Configuration Bot Discord
    BOT_PRESENCE_UPDATE_INTERVAL = 30  # secondes
    STATS_CACHE_TIMEOUT = 60  # secondes

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS en production

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///test_arsenal.db'

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
