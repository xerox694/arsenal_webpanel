# 🚀 Arsenal Bot - Déploiement Render

## 📋 Instructions Rapides

### 1. Préparer le Repository
```bash
git add .
git commit -m "🚀 Deploy Arsenal Bot to Render"
git push origin main
```

### 2. Configuration Render
1. Aller sur [render.com](https://render.com)
2. Connecter votre compte GitHub
3. Créer un nouveau **Web Service**
4. Sélectionner ce repository
5. Utiliser ces paramètres :

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python webpanel_advanced.py --start-bot --host=0.0.0.0 --port=$PORT --production
```

### 3. Variables d'Environnement Render
Ajouter dans l'interface Render :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DISCORD_TOKEN` | `votre_token_bot` | ⚠️ OBLIGATOIRE - Token Discord |
| `WEBPANEL_SECRET_KEY` | `votre_clé_secrète` | Clé secrète Flask (générer une clé forte) |
| `ENVIRONMENT` | `production` | Mode production |
| `LOG_LEVEL` | `INFO` | Niveau de logs |

### 4. Après Déploiement
- ✅ Bot Discord actif
- ✅ WebPanel accessible via l'URL Render
- ✅ Hot-reload disponible via WebPanel
- ✅ Logs en temps réel
- ✅ Toutes les fonctionnalités Arsenal

### 🔧 Commandes Git Utiles
```bash
# Pousser les changements
git add .
git commit -m "Update Arsenal Bot"
git push

# Render redéploie automatiquement !
```

### 🌐 Accès WebPanel
Une fois déployé, votre WebPanel sera accessible à :
`https://votre-app-name.onrender.com`

### 🆘 Support
Si problème, vérifier les logs Render et que `DISCORD_TOKEN` est bien configuré.

---
**Arsenal V4** - Bot Discord Ultra-Complet avec WebPanel 🚀
