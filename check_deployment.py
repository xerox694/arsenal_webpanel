#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VÉRIFICATEUR DEPLOYMENT RENDER
Vérifie que tout est prêt pour le déploiement
"""

import os
import sys
from pathlib import Path

def check_files():
    """Vérifier que tous les fichiers nécessaires existent"""
    required_files = [
        "main.py",
        "webpanel_advanced.py", 
        "requirements.txt",
        "Procfile",
        "render.yaml"
    ]
    
    print("📁 Vérification des fichiers...")
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} MANQUANT")
            return False
    return True

def check_env_vars():
    """Vérifier les variables d'environnement"""
    print("\n🔧 Variables d'environnement à configurer sur Render:")
    env_vars = {
        "DISCORD_TOKEN": "Token de votre bot Discord (OBLIGATOIRE)",
        "WEBPANEL_SECRET_KEY": "Clé secrète Flask (généré auto ou custom)",
        "ENVIRONMENT": "production",
        "LOG_LEVEL": "INFO"
    }
    
    for var, desc in env_vars.items():
        current = os.getenv(var)
        status = "✅" if current else "❌"
        print(f"{status} {var}: {desc}")
        if current:
            if var == "DISCORD_TOKEN":
                print(f"    Valeur: {current[:20]}...")
            else:
                print(f"    Valeur: {current}")

def check_procfile():
    """Vérifier le Procfile"""
    print("\n📋 Vérification Procfile...")
    if os.path.exists("Procfile"):
        with open("Procfile", "r") as f:
            content = f.read().strip()
            print(f"Contenu: {content}")
            if "--start-bot" in content:
                print("✅ Auto-start bot configuré")
            else:
                print("⚠️ Auto-start bot non configuré")
    else:
        print("❌ Procfile manquant")

def main():
    print("🚀 VÉRIFICATEUR DEPLOYMENT RENDER")
    print("=" * 50)
    
    all_good = True
    
    # Vérifier les fichiers
    if not check_files():
        all_good = False
    
    # Vérifier l'environnement
    check_env_vars()
    
    # Vérifier Procfile
    check_procfile()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ PRÊT POUR LE DÉPLOIEMENT!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. git add .")
        print("2. git commit -m 'Fix bot deployment'")
        print("3. git push origin main")
        print("4. Sur Render: Ajouter DISCORD_TOKEN dans Environment Variables")
        print("5. Redéployer le service")
    else:
        print("❌ PROBLÈMES DÉTECTÉS - Corrigez avant déploiement")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
