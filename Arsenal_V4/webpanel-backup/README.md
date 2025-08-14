# 🚀 ARSENAL V4 - WEBPANEL PRODUCTION

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## 🎯 Arsenal V4 - Dashboard Discord Bot Complet

**Webpanel de gestion avancé pour bot Discord Arsenal V4**

### ✨ Fonctionnalités

- 🎵 **Système Musical** - Contrôle audio avancé
- 🛡️ **Modération** - Outils de modération complets
- 🎰 **Casino** - Système de jeux intégré
- 📊 **Analytics** - Statistiques détaillées
- 🔧 **Administration** - Panel d'admin complet
- 🎨 **Interface Cyan** - Design neon moderne

### 🚀 Déploiement Render

1. **Fork ce repository**
2. **Connecte Render à ton GitHub**
3. **Crée un nouveau Web Service**
4. **Configure :**
   - **Root Directory:** `Arsenal_bot/Arsenal_V4/webpanel`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && gunicorn --bind 0.0.0.0:$PORT advanced_server:app --workers 1 --timeout 120`

5. **Variables d'environnement :**
   ```
   DISCORD_CLIENT_ID=1346646498040877076
   DISCORD_CLIENT_SECRET=TON_SECRET_DISCORD
   DISCORD_REDIRECT_URI=https://TON-APP.onrender.com/auth/callback
   ```

### 🌐 URLs disponibles

- `/` - Page de connexion Discord
- `/dashboard` - Dashboard principal
- `/casino` - Casino système
- `/api/stats` - API statistiques
- `/api/bot/status` - Statut du bot

### 🎨 Aperçu

Interface cyan neon avec sidebar complète, gestion multi-serveurs, authentification Discord OAuth2, casino intégré, métriques temps réel.

---

**🎯 Arsenal V4 - Production Ready !**