#!/bin/bash
# Arsenal V4 - Linux/Mac Launcher

echo "========================================="
echo "🚀 ARSENAL V4 - LAUNCHER AUTOMATIQUE"
echo "========================================="
echo ""
echo "🌐 WebPanel: http://localhost:5000"
echo "🤖 Bot Discord: Démarrage automatique"
echo "📊 Logs temps réel disponibles"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Veuillez installer Python 3"
    exit 1
fi

# Installer les dépendances
echo "📦 Vérification des dépendances..."
pip3 install flask flask-socketio requests > /dev/null 2>&1

# Créer les répertoires
mkdir -p templates static data logs

echo "✅ Dépendances vérifiées"
echo ""

# Démarrer le système
echo "🚀 Démarrage du système complet..."
echo "   - WebPanel sur http://localhost:5000"
echo "   - Bot Discord en arrière-plan"
echo "   - Logs en temps réel"
echo ""

# Lancer le webpanel avec auto-start du bot
python3 webpanel_advanced.py --start-bot

echo ""
echo "⚠️ Arrêt du système détecté"
