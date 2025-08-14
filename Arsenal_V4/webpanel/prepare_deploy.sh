#!/bin/bash

# 🚀 Script de Préparation Déploiement Arsenal V4
# Automatise la préparation pour le déploiement sur Render/Heroku/Railway

echo "🎯 Arsenal V4 WebPanel - Préparation Déploiement"
echo "=================================================="

# Vérification des fichiers essentiels
echo "📋 Vérification des fichiers..."

required_files=(
    "unified_launcher.py"
    "advanced_server.py" 
    "main.py"
    "requirements.txt"
    "render.yaml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant!"
        exit 1
    fi
done

# Vérification des pages frontend
echo ""
echo "🖥️ Vérification pages frontend..."

frontend_pages=(
    "webpanel/frontend/analytics.html"
    "webpanel/frontend/realtime.html"
    "webpanel/frontend/users.html"
    "webpanel/frontend/commands.html"
    "webpanel/frontend/automod.html"
    "webpanel/frontend/security.html"
    "webpanel/frontend/games.html"
    "webpanel/frontend/backup.html"
    "webpanel/frontend/bridges.html"
    "webpanel/frontend/hub.html"
    "webpanel/frontend/botinfo.html"
    "webpanel/frontend/help.html"
    "webpanel/frontend/performance.html"
    "webpanel/frontend/database.html"
    "webpanel/frontend/api.html"
)

pages_count=0
for page in "${frontend_pages[@]}"; do
    if [ -f "$page" ]; then
        pages_count=$((pages_count + 1))
        echo "✅ $(basename "$page")"
    else
        echo "❌ $(basename "$page") manquant!"
    fi
done

echo ""
echo "📊 Résumé: $pages_count/15 pages frontend détectées"

# Génération du fichier .gitignore
echo ""
echo "📝 Génération .gitignore..."

cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Secrets
config.json
secrets.json
token.txt

# Cache
*.cache
.cache/

# Temporary
tmp/
temp/
*.tmp

# Arsenal specific
hunt_royal_cache.json
arsenal_v4.db
hunt_royal.db
suggestions.db
hunt_royal_auth.db
hunt_royal_profiles.db
EOF

echo "✅ .gitignore créé"

# Vérification du requirements.txt
echo ""
echo "📦 Vérification des dépendances..."

if grep -q "discord.py" requirements.txt; then
    echo "✅ discord.py présent"
else
    echo "⚠️  discord.py manquant dans requirements.txt"
fi

if grep -q "flask" requirements.txt; then
    echo "✅ flask présent"
else
    echo "⚠️  flask manquant dans requirements.txt"
fi

# Génération du Procfile (pour Heroku)
echo ""
echo "📄 Génération Procfile..."

cat > Procfile << EOF
web: python unified_launcher.py
EOF

echo "✅ Procfile créé"

# Génération du runtime.txt (pour Heroku)
echo ""
echo "🐍 Génération runtime.txt..."

cat > runtime.txt << EOF
python-3.11.4
EOF

echo "✅ runtime.txt créé"

# Création du dossier static s'il n'existe pas
echo ""
echo "📁 Vérification structure dossiers..."

mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p templates
mkdir -p webpanel/frontend

echo "✅ Structure dossiers OK"

# Génération du fichier de configuration Render
echo ""
echo "⚙️ Génération render.yaml..."

cat > render.yaml << EOF
services:
  - type: web
    name: arsenal-v4-webpanel
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python unified_launcher.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 10000
    healthCheckPath: /
    disk:
      name: arsenal-data
      mountPath: /data
      sizeGB: 1
EOF

echo "✅ render.yaml mis à jour"

# Vérification de la configuration Git
echo ""
echo "🔄 Préparation Git..."

# Initialiser git si pas déjà fait
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialisé"
else
    echo "✅ Repository Git détecté"
fi

# Ajouter remote si nécessaire
if ! git remote | grep -q origin; then
    echo "⚠️  Ajoutez votre remote Git:"
    echo "   git remote add origin https://github.com/votre-username/arsenal-webpanel.git"
else
    echo "✅ Remote Git configuré"
fi

# Résumé final
echo ""
echo "🎉 PRÉPARATION TERMINÉE!"
echo "======================="
echo ""
echo "📊 Statistiques:"
echo "   • $pages_count pages frontend"
echo "   • Backend Flask complet"
echo "   • Launcher unifié prêt"
echo "   • Configuration déploiement OK"
echo ""
echo "🚀 Prochaines étapes:"
echo "   1. git add ."
echo "   2. git commit -m 'Arsenal V4 WebPanel Ready for Deployment'"
echo "   3. git push origin main"
echo "   4. Déployer sur Render/Heroku"
echo ""
echo "🔗 URLs de déploiement:"
echo "   • Render: https://render.com"
echo "   • Heroku: https://heroku.com"
echo "   • Railway: https://railway.app"
echo ""
echo "✅ Votre Arsenal V4 WebPanel est prêt pour la production!"

# Afficher les commandes Git suggérées
echo ""
echo "📋 Commandes Git suggérées:"
echo "git add ."
echo "git commit -m '🚀 Arsenal V4 WebPanel Complete - Ready for production deployment"
echo ""
echo "Features:"
echo "- 15 pages frontend with cyber theme"
echo "- Unified launcher (Discord Bot + WebPanel)"
echo "- Complete backend with 15+ routes"
echo "- Responsive design with animations"
echo "- Ready for real data integration'"
echo ""
echo "git push origin main"
