"""
🚀 ARSENAL V4 ULTIMATE - CONFIGURATION UNIFIÉE
==============================================

Configuration pour le service unique qui gère:
- Bot Discord Arsenal V4 Ultimate
- WebPanel intégré avec Gaming, AI, Music, Economy dans la sidebar
- Base de données partagée
- API unifiée

Version: 4.2.1 ULTIMATE
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class ArsenalConfig:
    """Configuration unifiée Arsenal V4 Ultimate"""
    
    # ==================== GÉNÉRAL ====================
    
    # Version
    VERSION = "4.2.1-ULTIMATE"
    APP_NAME = "Arsenal V4 Ultimate"
    
    # Environnement
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Ports et Host
    PORT = int(os.getenv('PORT', 10000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # ==================== DISCORD BOT ====================
    
    # Token Discord (OBLIGATOIRE)
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # OAuth Discord pour WebPanel
    DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '1346646498040877076')
    DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
    DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://arsenal-webpanel.onrender.com/auth/callback')
    
    # Permissions bot
    BOT_PERMISSIONS = 8  # Administrateur
    BOT_INTENTS = {
        'guilds': True,
        'members': True,
        'messages': True,
        'reactions': True,
        'voice_states': True,
        'presences': True,
        'message_content': True
    }
    
    # ==================== BASE DE DONNÉES ====================
    
    # Base de données SQLite
    DATABASE_URL = os.getenv('DATABASE_URL', './arsenal_v4.db')
    
    # Tables principales
    DB_TABLES = {
        'users': 'arsenal_users',
        'guilds': 'arsenal_guilds', 
        'economy': 'arsenal_economy',
        'games': 'arsenal_games',
        'music': 'arsenal_music',
        'ai': 'arsenal_ai',
        'logs': 'arsenal_logs'
    }
    
    # ==================== MODULES ULTIMATE ====================
    
    # Gaming Ultimate
    GAMING_CONFIG = {
        'casino_enabled': True,
        'quiz_enabled': True,
        'arcade_enabled': True,
        'rewards_multiplier': 1.5,
        'max_bet': 1000,
        'min_bet': 10
    }
    
    # AI Ultimate  
    AI_CONFIG = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'gpt-3.5-turbo',
        'max_tokens': 2000,
        'temperature': 0.7,
        'enabled': bool(os.getenv('OPENAI_API_KEY'))
    }
    
    # Music Ultimate
    MUSIC_CONFIG = {
        'youtube_enabled': True,
        'spotify_enabled': False,
        'max_queue_size': 100,
        'max_duration': 600,  # 10 minutes
        'volume_default': 50
    }
    
    # Economy Ultimate
    ECONOMY_CONFIG = {
        'currency_name': 'ArsenalCoins',
        'currency_symbol': 'AC',
        'daily_reward': 100,
        'work_min': 50,
        'work_max': 200,
        'bank_interest': 0.02  # 2% par jour
    }
    
    # ==================== WEBPANEL ====================
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'arsenal_v4_ultimate_secret_key_2024')
    SESSION_COOKIE_SECURE = ENVIRONMENT == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # WebSocket
    WEBSOCKET_ENABLED = True
    WEBSOCKET_LOGGER = DEBUG
    
    # ==================== SÉCURITÉ ====================
    
    # Administrateurs (IDs Discord)
    ADMIN_IDS = [
        123456789,  # Remplacer par vrais IDs
        int(os.getenv('CREATOR_ID', 0)) if os.getenv('CREATOR_ID') else None
    ]
    ADMIN_IDS = [aid for aid in ADMIN_IDS if aid]  # Retirer les None
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1 heure
    
    # Anti-spam
    ANTI_SPAM_ENABLED = True
    ANTI_SPAM_MAX_MESSAGES = 5
    ANTI_SPAM_TIME_WINDOW = 60  # 1 minute
    
    # ==================== LOGGING ====================
    
    # Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'arsenal_v4.log')
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Logs Discord
    DISCORD_LOG_CHANNEL = int(os.getenv('DISCORD_LOG_CHANNEL', 0)) if os.getenv('DISCORD_LOG_CHANNEL') else None
    
    # ==================== PERFORMANCE ====================
    
    # Cache
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 minutes
    
    # Threads
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    
    # Timeout
    HTTP_TIMEOUT = 30
    DB_TIMEOUT = 10
    
    # ==================== FONCTIONNALITÉS ====================
    
    # Modules activés
    ENABLED_MODULES = {
        'gaming': True,
        'ai': AI_CONFIG['enabled'],
        'music': True,
        'economy': True,
        'moderation': True,
        'fun': True,
        'utility': True,
        'admin': True
    }
    
    # Expérimental
    BETA_FEATURES = {
        'voice_ai': False,
        'image_generation': False,
        'blockchain_economy': False,
        'ar_features': False
    }
    
    # ==================== VALIDATION ====================
    
    @classmethod
    def validate(cls):
        """Valider la configuration"""
        errors = []
        
        # Discord token obligatoire
        if not cls.DISCORD_TOKEN:
            errors.append("❌ DISCORD_TOKEN manquant - Variable d'environnement requise")
        
        # Vérifier les IDs Discord
        if not cls.ADMIN_IDS:
            errors.append("⚠️ Aucun administrateur configuré")
        
        # AI Ultimate
        if cls.AI_CONFIG['enabled'] and not cls.AI_CONFIG['openai_api_key']:
            errors.append("⚠️ AI Ultimate activé mais OPENAI_API_KEY manquant")
        
        # OAuth Discord pour WebPanel
        if not cls.DISCORD_CLIENT_SECRET:
            errors.append("⚠️ DISCORD_CLIENT_SECRET manquant - WebPanel OAuth désactivé")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Afficher la configuration au démarrage"""
        print("🚀 Arsenal V4 Ultimate - Configuration")
        print("=" * 50)
        print(f"Version: {cls.VERSION}")
        print(f"Environnement: {cls.ENVIRONMENT}")
        print(f"Port: {cls.PORT}")
        print(f"Debug: {cls.DEBUG}")
        print()
        
        print("🤖 Discord Bot:")
        print(f"  Token: {'✅ Configuré' if cls.DISCORD_TOKEN else '❌ Manquant'}")
        print(f"  Client ID: {cls.DISCORD_CLIENT_ID}")
        print(f"  Admins: {len(cls.ADMIN_IDS)} configurés")
        print()
        
        print("🎮 Modules Ultimate:")
        for module, enabled in cls.ENABLED_MODULES.items():
            status = "✅" if enabled else "❌"
            print(f"  {module.title()}: {status}")
        print()
        
        print("🔧 Base de données:")
        print(f"  URL: {cls.DATABASE_URL}")
        print(f"  Tables: {len(cls.DB_TABLES)}")
        print()
        
        # Afficher les erreurs de validation
        errors = cls.validate()
        if errors:
            print("⚠️ Problèmes de configuration:")
            for error in errors:
                print(f"  {error}")
        else:
            print("✅ Configuration valide")
        
        print("=" * 50)

# Configuration globale
config = ArsenalConfig()
