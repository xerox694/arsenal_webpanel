# 🏹 Arsenal Bot V4 - Hunt Royal System

## 🎯 Vue d'ensemble

Arsenal Bot V4 avec système Hunt Royal complet incluant :
- **Hunt Royal Calculator** avec authentification token
- **Système de profils** avec web scraping
- **Bot Discord** avec commandes avancées
- **Webpanel** avec interface d'administration

## 🚀 Fonctionnalités

### 🔐 **Système d'Authentification**
- Enregistrement sécurisé avec vérifications anti-spam/raid
- Tokens uniques pour l'accès au calculator
- 4 niveaux d'accès (Member, VIP, Moderator, Admin)
- Statistiques admin détaillées

### 👤 **Hunt Royal Profiles**
- Linkage de comptes Hunt Royal
- Web scraping multi-sources
- Cache intelligent des données
- Interface Discord intégrée

### 🌐 **Webpanel**
- Hunt Royal Calculator avec authentification
- Dashboard administrateur
- API REST pour validation tokens
- Interface responsive

### 🤖 **Bot Discord**
- `/register` - Enregistrement sécurisé
- `/mytoken` - Récupération token
- `/hunt-stats` - Statistiques admin
- `/link-hunt` - Lier profil Hunt Royal
- `/profile-hunt` - Afficher profil
- `/unlink-hunt` - Délier profil

## 🛠️ Technologies

- **Backend**: Python 3.10+, Flask, SQLite
- **Discord**: discord.py, slash commands
- **Web Scraping**: aiohttp, BeautifulSoup
- **Frontend**: HTML5, CSS3, JavaScript
- **Déploiement**: Render.com, Git

## 📋 Installation

### Prérequis
```bash
Python 3.10+
Git
Discord Bot Token
```

### Dépendances
```bash
pip install -r requirements.txt
```

### Variables d'environnement
```env
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
SECRET_KEY=your_secret_key
```

## 🚀 Déploiement sur Render

1. **Fork ce repository**
2. **Connecter à Render.com**
3. **Créer Web Service**
   - Root Directory: `Arsenal_V4/webpanel`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT wsgi:application`
4. **Configurer variables d'environnement**
5. **Déployer** 🎉

## 📊 Commandes Discord

| Commande | Description | Permissions |
|----------|-------------|-------------|
| `/register` | S'enregistrer au système | Tous |
| `/mytoken` | Récupérer son token | Membre |
| `/hunt-stats` | Statistiques système | Admin |
| `/link-hunt` | Lier profil Hunt Royal | Membre |
| `/profile-hunt` | Voir profil Hunt Royal | Membre |
| `/unlink-hunt` | Délier profil | Membre |

## 🔐 Sécurité

- ✅ Anti-spam (comptes récents bloqués)
- ✅ Anti-raid (nouveaux membres protégés)
- ✅ Tokens sécurisés 32 caractères
- ✅ Logging complet des actions
- ✅ Validation multi-niveaux

## 📈 Statistiques

- Membres actifs par niveau
- Activité quotidienne/hebdomadaire
- Derniers enregistrements
- Répartition des rôles

## 🌐 URLs

- **Calculator**: https://your-app.onrender.com/calculator
- **Dashboard**: https://your-app.onrender.com/
- **API**: https://your-app.onrender.com/api/

## 📞 Support

Pour tout problème ou question :
- Créer une issue GitHub
- Contacter les administrateurs Discord
- Consulter la documentation

---

**Arsenal Bot V4** - Développé avec ❤️ pour la communauté Hunt Royal
