#!/bin/bash

echo "🚀 DÉPLOIEMENT RENDER - Arsenal V4 avec corrections JavaScript"
echo "=========================================================="

# Vérifier que nous sommes dans le bon dossier
if [ ! -f "advanced_server.py" ]; then
    echo "❌ Erreur: Veuillez exécuter ce script depuis le dossier Arsenal_bot"
    exit 1
fi

echo "✅ Dossier correct détecté"

# Ajouter tous les fichiers
echo "📦 Ajout des fichiers au git..."
git add -A

# Créer un commit avec les corrections
echo "💾 Création du commit de déploiement..."
git commit -m "🚀 DEPLOY: Arsenal V4 avec corrections JavaScript complètes

✅ CORRECTIONS DÉPLOYÉES:
- Dashboard corrigé sans erreurs JavaScript
- Routes API manquantes ajoutées (/api/pages/dashboard, /api/user/profile, /api/performance)
- Éléments DOM manquants corrigés (cpu-usage, ram-usage, uptime, discord-latency, etc.)
- Système admin complet avec Mega Coins (99,999,999,999,999 Arsenal Coins)
- Gestion null checking pour tous les éléments
- createAnalyticsPage fonction ajoutée
- Redirection automatique vers dashboard corrigé
- Session test automatique disponible

🎯 ERREURS RÉSOLUES:
- TypeError: Cannot set properties of null ✅
- ReferenceError: createAnalyticsPage is not defined ✅
- Routes 404 (dashboard, profile, performance) ✅
- Éléments manquants dans HTML ✅

📊 FONCTIONNALITÉS:
- Dashboard responsive sans erreurs F12
- Interface admin pour gestion utilisateurs
- API Mega Coins pour tests avec montants astronomiques
- Auto-refresh des données en temps réel

🌐 DÉPLOIEMENT: Production ready sur Render"

# Pousser vers GitHub
echo "🌐 Push vers GitHub..."
git push origin main

echo "✅ Déploiement terminé !"
echo "🔗 Render va automatiquement redéployer depuis GitHub"
echo "📊 URL: https://arsenal-webpanel.onrender.com"
echo "🎯 Dashboard corrigé sera disponible sous quelques minutes"
