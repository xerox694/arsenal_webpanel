#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier les variables d'environnement sur Render
"""
import os
import sys

print("=== DIAGNOSTIC VARIABLES D'ENVIRONNEMENT ===")
print(f"Python version: {sys.version}")
print(f"Plateforme: {sys.platform}")
print()

print("=== VARIABLES DISCORD ===")
discord_vars = [
    'DISCORD_CLIENT_ID',
    'DISCORD_CLIENT_SECRET', 
    'DISCORD_REDIRECT_URI'
]

for var in discord_vars:
    value = os.environ.get(var)
    if value:
        if 'SECRET' in var:
            print(f"{var}: ***masqué*** (longueur: {len(value)})")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: ❌ NON DÉFINIE")

print()
print("=== TOUTES LES VARIABLES D'ENVIRONNEMENT ===")
all_vars = list(os.environ.keys())
discord_related = [var for var in all_vars if 'DISCORD' in var.upper()]

if discord_related:
    print("Variables contenant 'DISCORD':")
    for var in discord_related:
        value = os.environ.get(var)
        if 'SECRET' in var.upper():
            print(f"  {var}: ***masqué***")
        else:
            print(f"  {var}: {value}")
else:
    print("❌ Aucune variable contenant 'DISCORD' trouvée")

print()
print("=== VARIABLES RENDER ===")
render_vars = [var for var in all_vars if var.startswith('RENDER_')]
if render_vars:
    print("Variables Render détectées:")
    for var in render_vars:
        print(f"  {var}: {os.environ.get(var)}")
else:
    print("Aucune variable Render détectée")

print()
print("=== TOTAL VARIABLES ===")
print(f"Nombre total de variables d'environnement: {len(all_vars)}")
