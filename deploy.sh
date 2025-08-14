#!/bin/bash
# 🚀 Script de déploiement Arsenal V4 sur Render

echo "🚀 Arsenal V4 - Déploiement Render"
echo "=================================="

# Vérification Git
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

# Initialisation Git si nécessaire
if [ ! -d ".git" ]; then
    echo "📦 Initialisation du repository Git..."
    git init
    git branch -M main
fi

# Ajouter tous les fichiers
echo "📁 Ajout des fichiers..."
git add .

# Commit
echo "💾 Commit des changements..."
git commit -m "🚀 Arsenal V4 - Configuration complète pour Render"

# Configuration remote (à modifier avec votre URL)
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Configuration remote GitHub..."
    echo "⚠️  Configurez votre remote GitHub:"
    echo "   git remote add origin https://github.com/xerox694/arsenal_webpanel.git"
    echo "   git push -u origin main"
else
    echo "📤 Push vers GitHub..."
    git push origin main
fi

echo ""
echo "✅ Préparation terminée !"
echo ""
echo "🌐 Étapes suivantes:"
echo "1. Aller sur render.com"
echo "2. Connecter votre repository GitHub" 
echo "3. Configurer les variables d'environnement"
echo "4. Déployer !"
echo ""
echo "📖 Documentation complète: DEPLOY_RENDER_GUIDE.md"
