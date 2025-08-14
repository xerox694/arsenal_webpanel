# 🌐 GUIDE DE DÉPLOIEMENT PUBLIC ARSENAL V4

## 🚀 **DÉPLOIEMENT SUR RENDER.COM (GRATUIT)**

### 1. **Préparation des fichiers**

Créez un `render.yaml` :
```yaml
services:
  - type: web
    name: arsenal-v4-webpanel
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:application
    envVars:
      - key: DISCORD_CLIENT_ID
        value: YOUR_DISCORD_CLIENT_ID
      - key: DISCORD_CLIENT_SECRET
        value: YOUR_DISCORD_CLIENT_SECRET
      - key: DISCORD_BOT_TOKEN
        value: YOUR_DISCORD_BOT_TOKEN
      - key: SECRET_KEY
        value: YOUR_SECRET_KEY
```

### 2. **Via GitHub + Render**
1. **Poussez votre code sur GitHub**
2. **Connectez-vous sur render.com**
3. **Créez un nouveau Web Service**
4. **Connectez votre repo GitHub**
5. **Configurez les variables d'environnement**

### 3. **URL publique générée**
Render vous donnera une URL comme:
`https://arsenal-v4-webpanel.onrender.com`

---

## 🌐 **DÉPLOIEMENT SUR RAILWAY.APP**

### 1. **Installation**
```bash
npm install -g @railway/cli
railway login
```

### 2. **Déploiement**
```bash
cd "a:\Arsenal_bot\Arsenal_V4\webpanel"
railway deploy
```

### 3. **URL publique**
Railway génère: `https://arsenal-v4-xxxxx.railway.app`

---

## 🌐 **DÉPLOIEMENT SUR HEROKU**

### 1. **Créer un Procfile**
```
web: gunicorn wsgi:application
```

### 2. **Déploiement**
```bash
heroku create arsenal-v4-webpanel
git push heroku main
heroku config:set DISCORD_CLIENT_ID=YOUR_DISCORD_CLIENT_ID
heroku config:set DISCORD_CLIENT_SECRET=YOUR_DISCORD_CLIENT_SECRET
```

### 3. **URL publique**
`https://arsenal-v4-webpanel.herokuapp.com`

---

## 🏠 **HÉBERGEMENT PERSONNEL (VPS)**

### 1. **Serveur Ubuntu/Debian**
```bash
# Installation
sudo apt update
sudo apt install python3 python3-pip nginx
git clone https://github.com/votre-repo/arsenal-v4
cd arsenal-v4/webpanel

# Installation des dépendances
pip3 install -r requirements.txt

# Lancement avec Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:application
```

### 2. **Configuration Nginx**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔗 **DOMAINES PERSONNALISÉS**

### Cloudflare (Gratuit)
1. **Achetez un domaine** (ex: arsenal-v4.com)
2. **Configurez DNS** pour pointer vers votre serveur
3. **SSL automatique** avec Cloudflare

### Freenom (Domaines gratuits)
1. **Obtenez un .tk/.ml/.ga** gratuit
2. **Configurez DNS** 
3. **Pointez vers votre hébergement**

---

## ⚡ **DÉPLOIEMENT RAPIDE RECOMMANDÉ**

**RENDER.COM** est le plus simple:
1. **Créez un compte** sur render.com
2. **Connectez GitHub**
3. **Auto-déploiement** à chaque commit
4. **SSL inclus**
5. **URL publique instantanée**

**Avantages:**
- ✅ **Gratuit** jusqu'à 750h/mois
- ✅ **SSL automatique**
- ✅ **Redémarrage auto**
- ✅ **Base de données gratuite**
- ✅ **Logs en temps réel**

---

## 🔧 **CONFIGURATION POUR PRODUCTION**

Modifiez votre `.env` pour la production:
```env
FLASK_ENV=production
DEBUG=false
DOMAIN=arsenal-v4-webpanel.onrender.com
DISCORD_REDIRECT_URI=https://arsenal-v4-webpanel.onrender.com/auth/callback
```

---

## 🎯 **ÉTAPES FINALES**

1. **Choisissez votre plateforme** (Render recommandé)
2. **Configurez les variables d'environnement**
3. **Déployez votre code**
4. **Testez l'URL publique**
5. **Configurez votre bot Discord** avec la nouvelle URL

**🌐 Votre webpanel sera accessible publiquement dans le monde entier !**
