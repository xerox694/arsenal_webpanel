#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier les variables d'environnement sur Render
"""

import os
import sys

def check_env_variables():
    """Vérifier les variables d'environnement critiques"""
    
    required_vars = {
        'DISCORD_CLIENT_ID': 'ID Client Discord',
        'DISCORD_CLIENT_SECRET': 'Secret Client Discord', 
        'DISCORD_REDIRECT_URI': 'URI de redirection Discord',
        'DISCORD_BOT_TOKEN': 'Token du bot Discord',
        'SECRET_KEY': 'Clé secrète Flask',
        'CREATOR_ID': 'ID du créateur',
        'ADMIN_IDS': 'IDs des administrateurs',
        'BOT_SERVERS': 'Serveurs du bot'
    }
    
    optional_vars = {
        'DEBUG': 'Mode debug',
        'ALLOWED_ORIGINS': 'Origines autorisées CORS',
        'BYPASS_ALLOWED_IPS': 'IPs autorisées bypass',
        'BYPASS_SECRET_TOKEN': 'Token secret bypass'
    }
    
    print("🔍 DIAGNOSTIC DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 50)
    
    missing_vars = []
    
    # Vérifier les variables requises
    print("\n📋 VARIABLES REQUISES:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Masquer les valeurs sensibles
            if any(sensitive in var.lower() for sensitive in ['secret', 'token', 'key']):
                display_value = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: MANQUANT")
            missing_vars.append(var)
    
    # Vérifier les variables optionnelles
    print("\n📋 VARIABLES OPTIONNELLES:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: Non défini (utilise valeur par défaut)")
    
    # Vérifications spécifiques
    print("\n🔧 VÉRIFICATIONS SPÉCIFIQUES:")
    
    # Discord OAuth
    discord_redirect = os.getenv('DISCORD_REDIRECT_URI')
    if discord_redirect:
        if 'onrender.com' in discord_redirect:
            print("  ✅ DISCORD_REDIRECT_URI: Utilise bien onrender.com")
        else:
            print("  ⚠️  DISCORD_REDIRECT_URI: Ne semble pas utiliser onrender.com")
    
    # Bot servers
    bot_servers = os.getenv('BOT_SERVERS', '')
    server_count = len(bot_servers.split(',')) if bot_servers else 0
    print(f"  📊 BOT_SERVERS: {server_count} serveur(s) configuré(s)")
    
    # Admin IDs
    admin_ids = os.getenv('ADMIN_IDS', '')
    admin_count = len(admin_ids.split(',')) if admin_ids else 0
    print(f"  👑 ADMIN_IDS: {admin_count} administrateur(s) configuré(s)")
    
    print("\n" + "=" * 50)
    
    if missing_vars:
        print(f"❌ {len(missing_vars)} variable(s) manquante(s): {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Toutes les variables requises sont présentes")
        return True

if __name__ == '__main__':
    success = check_env_variables()
    sys.exit(0 if success else 1)
