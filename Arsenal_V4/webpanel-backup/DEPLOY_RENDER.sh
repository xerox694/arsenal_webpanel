#!/bin/bash

# 🚀 Script de déploiement automatique Render
# Arsenal V4 Webpanel - Prêt pour la production !

echo "🚀 DÉPLOIEMENT ARSENAL V4 WEBPANEL SUR RENDER"
echo "=============================================="

# Variables de configuration
APP_NAME="arsenal-v4-webpanel"
GITHUB_REPO="xerox3elite/arsenal-v4-webpanel"
ROOT_DIR="Arsenal_bot/Arsenal_V4/webpanel"

echo "📋 Configuration détectée :"
echo "   📱 App Name: $APP_NAME"
echo "   📦 GitHub Repo: $GITHUB_REPO"
echo "   📁 Root Directory: $ROOT_DIR"
echo ""

# Vérification des fichiers requis
echo "🔍 Vérification des fichiers de déploiement..."

FILES_REQUIRED=(
    "requirements.txt"
    "Procfile"
    "start.sh"
    "backend/advanced_server.py"
    "advanced_interface.html"
    "login.html"
)

for file in "${FILES_REQUIRED[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - MANQUANT !"
        exit 1
    fi
done

echo ""
echo "🎯 INSTRUCTIONS POUR RENDER :"
echo "=============================================="
echo ""
echo "1. 🌐 Va sur https://render.com et connecte-toi"
echo ""
echo "2. 🔗 Clique 'New +' → 'Web Service'"
echo ""
echo "3. 📦 Connecte ton repository GitHub :"
echo "   Repository: $GITHUB_REPO"
echo ""
echo "4. ⚙️ Configuration Render :"
echo "   Name: $APP_NAME"
echo "   Root Directory: $ROOT_DIR"
echo "   Environment: Python 3"
echo "   Build Command: pip install -r requirements.txt"
echo "   Start Command: cd backend && gunicorn --bind 0.0.0.0:\$PORT advanced_server:app --workers 1 --timeout 120"
echo ""
echo "5. 🔐 Variables d'environnement à ajouter :"
echo "   DISCORD_CLIENT_ID=1346646498040877076"
echo "   DISCORD_CLIENT_SECRET=TON_VRAI_SECRET_DISCORD"
echo "   DISCORD_REDIRECT_URI=https://TON-APP.onrender.com/auth/callback"
echo ""
echo "6. 🚀 Clique 'Create Web Service' !"
echo ""
echo "🎉 RÉSULTAT ATTENDU :"
echo "=============================================="
echo "✅ Dashboard complet avec sidebar"
echo "✅ Authentification Discord OAuth2"
echo "✅ APIs RESTful fonctionnelles"
echo "✅ Base de données SQLite persistante"
echo "✅ Gestion serveurs Discord"
echo "✅ Métriques temps réel"
echo "✅ Système de casino intégré"
echo "✅ Interface responsive"
echo ""
echo "🌐 URLs disponibles après déploiement :"
echo "   https://TON-APP.onrender.com/ - Page de connexion"
echo "   https://TON-APP.onrender.com/dashboard - Dashboard principal"
echo "   https://TON-APP.onrender.com/casino - Casino"
echo "   https://TON-APP.onrender.com/api/stats - API statistiques"
echo ""
echo "🎯 TON WEBPANEL ARSENAL V4 EST PRÊT POUR LA PRODUCTION !"
echo "💪 Développé et optimisé par GitHub Copilot"
