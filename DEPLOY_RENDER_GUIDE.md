# Déploiement Arsenal V4 sur Render.com

## 📋 Guide Complet de Déploiement

### 🚀 Étapes de Déploiement Rapide

#### 1. Préparation du Repository GitHub

```bash
# Créer et configurer le repo GitHub
git init
git add .
git commit -m "🚀 Arsenal V4 - Configuration complète pour Render"
git branch -M main
git remote add origin https://github.com/xerox694/arsenal_webpanel.git
git push -u origin main
```

#### 2. Configuration sur Render.com

1. **Connecter le Repository:**
   - Aller sur [render.com](https://render.com)
   - Créer un compte ou se connecter
   - Cliquer "New +" → "Web Service"
   - Connecter votre repository GitHub

2. **Configuration Automatique:**
   - Render détectera automatiquement le fichier `render.yaml`
   - La configuration sera appliquée automatiquement
   - Service name: `arsenal-webpanel`

#### 3. Variables d'Environnement Obligatoires

Dans le dashboard Render, configurer ces variables:

```env
# 🔑 OBLIGATOIRE - Token du bot Discord
DISCORD_TOKEN=votre_token_bot_discord

# 🔑 OBLIGATOIRE - ID de l'application Discord
DISCORD_CLIENT_ID=votre_client_id

# 🔑 OBLIGATOIRE - Secret de l'application Discord  
DISCORD_CLIENT_SECRET=votre_client_secret

# ⚙️ Configuration automatique (déjà définie)
BOT_PREFIX=!
FLASK_ENV=production
DEBUG=false
ARSENAL_MODE=production
WEB_AUTH_ENABLED=true
MAX_LOG_LINES=1000
AUTO_RESTART=true
```

### 🔧 Configuration Discord

1. **Créer une Application Discord:**
   - Aller sur [Discord Developer Portal](https://discord.com/developers/applications)
   - Créer une nouvelle application
   - Noter le **Client ID**

2. **Configurer le Bot:**
   - Section "Bot" → Créer un bot
   - Noter le **Token** (gardez-le secret!)
   - Activer les intents nécessaires:
     - Message Content Intent
     - Server Members Intent
     - Presence Intent

3. **OAuth2 URLs:**
   - Section "OAuth2" → "General"
   - Ajouter l'URL de redirection: `https://arsenal-webpanel.onrender.com/auth/callback`
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Administrator` (ou permissions spécifiques)

### 🌐 URLs après Déploiement

- **WebPanel:** `https://arsenal-webpanel.onrender.com`
- **Bot Status:** `https://arsenal-webpanel.onrender.com/api/status`
- **Logs:** `https://arsenal-webpanel.onrender.com/logs`

### 📊 Monitoring & Logs

Le WebPanel intégré offre:
- ✅ Statut en temps réel du bot
- 📋 Logs streaming en direct
- 🔄 Hot-reload des modules
- 📈 Métriques de performance
- 🛡️ Interface d'administration

### 🔄 Mises à jour

Pour déployer une mise à jour:

```bash
git add .
git commit -m "🔄 Mise à jour Arsenal V4"
git push origin main
```

Render redéploiera automatiquement.

### ⚡ Performance & Limites

**Plan Starter (Recommandé):**
- ✅ 512MB RAM
- ✅ 0.5 CPU
- ✅ SSL automatique
- ✅ Domaine personnalisé possible
- ✅ 750h/mois gratuites

**Optimisations incluses:**
- 🔧 Logs rotatifs (max 1000 lignes)
- 🔧 Redémarrage automatique
- 🔧 Gestion mémoire optimisée
- 🔧 Mode production activé

### 🆘 Dépannage

**Bot ne démarre pas:**
1. Vérifier le `DISCORD_TOKEN`
2. Vérifier les permissions du bot
3. Consulter les logs: Section "Logs" sur Render

**WebPanel inaccessible:**
1. Vérifier le déploiement (statut vert)
2. Attendre ~2min après déploiement
3. Vérifier l'URL: `https://arsenal-webpanel.onrender.com`

**Erreurs communes:**
- `DISCORD_TOKEN` manquant → Ajouter dans les variables d'environnement
- `Port binding error` → Render gère automatiquement le port
- `Module import error` → Vérifier `requirements.txt`

### 🔐 Sécurité

- ✅ Token Discord chiffré
- ✅ Variables d'environnement sécurisées
- ✅ HTTPS obligatoire
- ✅ Authentication WebPanel
- ✅ Logs sensibles filtrés

### 📞 Support

En cas de problème:
1. Consulter les logs Render
2. Vérifier la configuration Discord
3. Tester en local avec `python webpanel_advanced.py --start-bot`

---

**🎉 Une fois déployé, votre bot Arsenal sera accessible 24/7 avec une interface web complète !**
