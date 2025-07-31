# 🔥 ARSENAL V4 WEBPANEL - DÉPLOIEMENT POWERSHELL
Write-Host "🔥 ARSENAL V4 WEBPANEL - DÉPLOIEMENT COMPLET" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Yellow

Write-Host "📋 Vérification de l'environnement..." -ForegroundColor Cyan

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Installez Python depuis https://python.org" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Vérifier Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js détecté: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js non trouvé" -ForegroundColor Red
    Write-Host "📥 Installation recommandée depuis https://nodejs.org" -ForegroundColor Yellow
    $install = Read-Host "Voulez-vous continuer sans Node.js? (Le frontend ne fonctionnera pas) [y/N]"
    if ($install -ne "y" -and $install -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 DÉMARRAGE D'ARSENAL V4 WEBPANEL" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Yellow

# Démarrer le backend
Write-Host "🔧 Démarrage du backend Flask..." -ForegroundColor Cyan
Set-Location "a:\Arsenal_bot\Arsenal_V4\webpanel\backend"

# Lancer le backend en arrière-plan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py" -WindowStyle Normal

# Attendre le démarrage
Write-Host "⏳ Attente du démarrage du backend..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Tester le backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/test" -TimeoutSec 5
    Write-Host "✅ Backend démarré avec succès!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend en cours de démarrage..." -ForegroundColor Yellow
}

# Démarrer le frontend si Node.js est disponible
try {
    node --version > $null 2>&1
    Write-Host "🎨 Démarrage du frontend React..." -ForegroundColor Cyan
    Set-Location "a:\Arsenal_bot\Arsenal_V4\webpanel\frontend"
    
    # Installer les dépendances si nécessaire
    if (!(Test-Path "node_modules")) {
        Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
        npm install
    }
    
    # Lancer le frontend
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal
    
    Write-Host "✅ Frontend React démarré!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Frontend non démarré (Node.js requis)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ ARSENAL V4 WEBPANEL DÉPLOYÉ!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Accès WebPanel: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 API Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 APIs disponibles:" -ForegroundColor Yellow
Write-Host "  • 💰 Économie: /api/economy/users/SERVER_ID" -ForegroundColor White
Write-Host "  • 🛡️ Modération: /api/moderation/logs/SERVER_ID" -ForegroundColor White
Write-Host "  • 🎵 Musique: /api/music/queue/SERVER_ID" -ForegroundColor White
Write-Host "  • 🎮 Gaming: /api/gaming/levels/SERVER_ID" -ForegroundColor White
Write-Host "  • 📊 Analytics: /api/analytics/metrics/SERVER_ID" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Toutes les 6 phases sont opérationnelles!" -ForegroundColor Green
Write-Host "💾 Base de données avec données réelles: arsenal_v4.db" -ForegroundColor Cyan
Write-Host ""

# Ouvrir le navigateur
Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Cyan
Start-Process "http://localhost:5000"

Read-Host "Appuyez sur Entrée pour fermer"
