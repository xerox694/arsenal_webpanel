#!/bin/bash

# Script de démarrage pour Render
echo "🚀 Démarrage Arsenal V4 Webpanel sur Render..."

# Installation des dépendances si nécessaire
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Navigation vers le dossier backend
cd backend

# Démarrage du serveur avec Gunicorn
echo "🌐 Lancement du serveur..."
gunicorn --bind 0.0.0.0:$PORT advanced_server:app --workers 1 --timeout 120
