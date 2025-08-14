# 🚀 Arsenal V4 WebPanel Backend

Backend Flask complet pour Arsenal V4 WebPanel avec toutes les APIs nécessaires.

## 🎯 Structure

```
backend/
├── app.py                 # Application Flask principale
├── config.py             # Configuration
├── requirements.txt      # Dépendances Python
├── models/              
│   ├── __init__.py
│   ├── database.py       # Base de données
│   ├── user.py           # Modèle utilisateur
│   └── server.py         # Modèle serveur
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentification Discord OAuth
│   ├── api.py            # APIs principales
│   ├── admin.py          # Routes admin
│   └── stats.py          # Statistiques
├── services/
│   ├── __init__.py
│   ├── discord_bot.py    # Interface avec le bot Discord
│   ├── oauth.py          # Service OAuth Discord
│   └── cache.py          # Cache Redis
└── utils/
    ├── __init__.py
    ├── decorators.py     # Décorateurs (auth, permissions)
    └── helpers.py        # Fonctions utilitaires
```

## 🔧 Fonctionnalités

### ✅ Authentification
- OAuth Discord complet
- Sessions sécurisées
- Gestion des permissions

### ✅ APIs
- `/api/stats` - Statistiques du bot
- `/api/bot/status` - Statut du bot
- `/api/servers` - Gestion des serveurs
- `/api/users` - Gestion des utilisateurs
- `/api/music` - Système musical
- `/api/admin` - Fonctions admin

### ✅ Temps Réel
- WebSockets pour les mises à jour live
- Cache Redis pour les performances
- Monitoring en temps réel

## 🚀 Installation

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend disponible sur `http://localhost:5000`
