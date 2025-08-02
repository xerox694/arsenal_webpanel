#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de variables d'environnement pour Arsenal WebPanel
"""

import secrets
import string

def generate_secret_key(length=120):
    """Générer une clé secrète ultra-sécurisée"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_bypass_token(length=64):
    """Générer un token de bypass sécurisé"""
    return secrets.token_urlsafe(length)

print("🔐 GÉNÉRATEUR DE VARIABLES D'ENVIRONNEMENT ARSENAL WEBPANEL")
print("=" * 70)

print("\n📝 COPIEZ CES VARIABLES DANS VOTRE CONFIGURATION RENDER :")
print("=" * 70)

# Générer SECRET_KEY ultra-sécurisée
secret_key = generate_secret_key(120)
print(f"SECRET_KEY={secret_key}")

# Générer BYPASS_SECRET_TOKEN
bypass_token = generate_bypass_token(64)
print(f"BYPASS_SECRET_TOKEN={bypass_token}")

print("\n🎯 VARIABLES DISCORD À CONFIGURER MANUELLEMENT :")
print("=" * 70)
print("# Allez sur https://discord.com/developers/applications")
print("# Créez/sélectionnez votre application")
print("# Dans OAuth2 > General :")

print("DISCORD_CLIENT_ID=VOTRE_CLIENT_ID_ICI")
print("DISCORD_CLIENT_SECRET=VOTRE_CLIENT_SECRET_ICI")
print("DISCORD_REDIRECT_URI=https://arsenal-webpanel.onrender.com/auth/callback")

print("\n# Dans Bot :")
print("DISCORD_BOT_TOKEN=VOTRE_BOT_TOKEN_ICI")

print("\n🎛️ CONFIGURATION UTILISATEURS :")
print("=" * 70)
print("# Votre ID Discord (clic droit sur votre profil > Copier l'ID)")
print("CREATOR_ID=VOTRE_DISCORD_ID_ICI")

print("\n# IDs Discord des admins (séparés par des virgules)")
print("ADMIN_IDS=id1,id2,id3")

print("\n# IDs des serveurs Discord du bot (séparés par des virgules)")
print("BOT_SERVERS=server_id1,server_id2,server_id3")

print("\n⚙️ VARIABLES OPTIONNELLES :")
print("=" * 70)
print("DEBUG=False")
print("ALLOWED_ORIGINS=https://arsenal-webpanel.onrender.com")

print("\n" + "=" * 70)
print("🚨 IMPORTANT :")
print("1. Remplacez TOUS les 'VOTRE_XXX_ICI' par vos vraies valeurs")
print("2. Dans Discord Developer Portal, ajoutez cette URL de redirection :")
print("   https://arsenal-webpanel.onrender.com/auth/callback")
print("3. Après configuration, testez : https://arsenal-webpanel.onrender.com/debug/env")
print("=" * 70)

print(f"\n✅ SECRET_KEY générée : {len(secret_key)} caractères")
print(f"✅ BYPASS_TOKEN généré : {len(bypass_token)} caractères (base64)")
print("🔒 Ces clés sont cryptographiquement sécurisées !")
