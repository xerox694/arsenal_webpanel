#!/bin/bash
# 🚀 Script de déploiement Arsenal Bot V4
# Remplacez YOUR_USERNAME par votre nom d'utilisateur GitHub

echo "🏹 Arsenal Bot V4 - Déploiement GitHub"
echo "======================================"

# Vérifier les commits
echo "📋 Commits actuels :"
git log --oneline -5

echo ""
echo "🔗 Ajout du remote GitHub..."
# REMPLACEZ 'YOUR_USERNAME' par votre nom d'utilisateur GitHub !
git remote add origin https://github.com/YOUR_USERNAME/arsenal-bot-v4-hunt-royal.git

echo "🌐 Push vers GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Code poussé sur GitHub !"
echo "🌐 Rendez-vous sur https://github.com/YOUR_USERNAME/arsenal-bot-v4-hunt-royal"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Aller sur render.com"
echo "2. Connecter votre repository GitHub"
echo "3. Créer un Web Service"
echo "4. Root Directory: Arsenal_V4/webpanel"
echo "5. Configurer les variables d'environnement"
echo ""
echo "🎯 Variables d'environnement à configurer sur Render :"
echo "- DISCORD_CLIENT_ID"
echo "- DISCORD_CLIENT_SECRET"
echo "- DISCORD_BOT_TOKEN"
echo "- SECRET_KEY"
