# 🏹 Arsenal Bot V4 - Déploiement sur Render

## Instructions de déploiement

### 1. Repository GitHub
```bash
# Remplacez YOUR_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/YOUR_USERNAME/arsenal-bot-v4.git
git branch -M main
git push -u origin main
```

### 2. Configuration Render

1. Allez sur [render.com](https://render.com)
2. Connectez votre repository GitHub
3. Créez un nouveau **Web Service**
4. Sélectionnez le dossier `Arsenal_V4/webpanel` comme Build & Deploy
5. Configurez les variables d'environnement :

**Variables d'environnement requises :**
- `DISCORD_CLIENT_ID` : ID de votre application Discord
- `DISCORD_CLIENT_SECRET` : Secret de votre application Discord  
- `DISCORD_BOT_TOKEN` : Token de votre bot Discord
- `DISCORD_REDIRECT_URI` : https://VOTRE-APP.onrender.com/callback
- `SECRET_KEY` : Clé secrète Flask (générée automatiquement)

### 3. Configuration Build

- **Build Command :** `pip install -r requirements.txt`
- **Start Command :** `gunicorn --bind 0.0.0.0:$PORT wsgi:application`
- **Root Directory :** `Arsenal_V4/webpanel`

### 4. Test du déploiement

Une fois déployé, testez :
- Page de login : https://VOTRE-APP.onrender.com/
- Calculator Hunt Royal : https://VOTRE-APP.onrender.com/calculator

## Structure des fichiers pour Render

```
Arsenal_V4/webpanel/
├── requirements.txt    # Dépendances Python
├── wsgi.py            # Point d'entrée WSGI
├── app.py             # Application Flask principale
├── render.yaml        # Configuration Render
├── Procfile           # Alternative pour le déploiement
└── backend/           # Code backend avec routes API
```

## Commandes Discord liées

- `/register` : S'enregistrer pour obtenir un token
- `/mytoken` : Récupérer son token d'accès
- `/link-hunt username` : Lier son profil Hunt Royal
- `/profile-hunt` : Voir son profil Hunt Royal

## 🔧 Debug et logs

Render fournit des logs en temps réel pour debugger les problèmes de déploiement.
