#!/usr/bin/env python3
"""
🚀 Fichier app.py - Point d'entrée pour Render.com
Redirige vers l'application principale dans backend/advanced_server.py
"""
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_path / "backend"))

print("🚀 app.py: Redirection vers Arsenal V4 WebPanel...")

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Importer l'application depuis advanced_server
try:
    from backend.advanced_server import app
    print("✅ app.py: Application importée depuis advanced_server.py")
except ImportError as e:
    print(f"❌ app.py: Erreur import advanced_server: {e}")
    raise

# Exposition pour Gunicorn - IMPORTANT: doit s'appeler 'app'
# C'est cette variable que Gunicorn cherche avec 'app:app'
# app = l'instance Flask importée

if __name__ == "__main__":
    print("🚀 app.py: Démarrage direct de l'application")
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
