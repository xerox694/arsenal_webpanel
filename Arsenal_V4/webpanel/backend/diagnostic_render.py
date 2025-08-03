#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNOSTIC RENDER - Version check
"""

import os
from datetime import datetime

print("🔍 DIAGNOSTIC RENDER DEPLOY")
print("=" * 50)
print(f"⏰ Timestamp: {datetime.now()}")
print(f"🌍 Environment: {os.getenv('RENDER', 'LOCAL')}")
print(f"🔢 Version: 4.3.0 - DEPLOY FORCE")
print(f"📍 Path: {os.getcwd()}")
print(f"📁 Files in current dir: {os.listdir('.')}")

# Test simple d'import
try:
    print("\n🧪 Test import app...")
    import sys
    sys.path.append('.')
    
    # Définir les variables d'environnement pour éviter l'erreur
    os.environ['DISCORD_CLIENT_ID'] = '1346646498040877076'
    os.environ['DISCORD_CLIENT_SECRET'] = 'test_secret'
    os.environ['DISCORD_REDIRECT_URI'] = 'http://localhost:5000/auth/callback'
    
    from app import app
    print("✅ Import app réussi")
    
    # Compter les routes
    routes_count = len(list(app.url_map.iter_rules()))
    print(f"📊 Nombre de routes: {routes_count}")
    
    # Routes critiques
    critical_routes = ['/api/auth/user', '/auth/discord', '/NSS', '/huntroyale/demo']
    for route in app.url_map.iter_rules():
        if route.rule in critical_routes:
            print(f"✅ {route.rule} -> {route.endpoint}")
    
except Exception as e:
    print(f"❌ Erreur import: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 DIAGNOSTIC TERMINÉ")
