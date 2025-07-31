# 🔥 ARSENAL V4 WEBPANEL - GUIDE DE DÉPLOIEMENT

## 🎯 Vue d'ensemble

Arsenal V4 WebPanel est un système de gestion web complet avec **6 phases opérationnelles** :
- **Phase 1** : Dashboard & Base ✅
- **Phase 2** : EconomyManager + APIs + BDD ✅
- **Phase 3** : ModerationManager + APIs + BDD ✅
- **Phase 4** : MusicManager + APIs + BDD ✅
- **Phase 5** : GamingManager + APIs + BDD ✅
- **Phase 6** : AnalyticsManager + APIs + BDD ✅

## 🚀 Déploiement Rapide

### Option 1 : Script Automatique (Recommandé)
```batch
# Double-cliquez sur le fichier ou exécutez :
deploy_arsenal_v4.bat
```

### Option 2 : PowerShell
```powershell
# Clic droit > "Exécuter avec PowerShell" ou :
.\deploy_arsenal_v4.ps1
```

### Option 3 : Manuel

#### Backend (Requis)
```bash
cd backend
python app.py
```

#### Frontend (Optionnel - nécessite Node.js)
```bash
cd frontend
npm install
npm start
```

## 📋 Prérequis

### ✅ Requis
- **Python 3.8+** avec pip
- **Windows 10/11** (PowerShell)

### 🎨 Optionnel (pour l'interface web)
- **Node.js 18+** avec npm

## 🌐 Accès

Une fois déployé :
- **WebPanel** : http://localhost:3000 (avec Node.js)
- **API Backend** : http://localhost:5000
- **Test API** : http://localhost:5000/api/test

## 📊 APIs Disponibles

### Phase 2 : Économie
- `GET /api/economy/users/{server_id}` - Utilisateurs économie
- `GET /api/economy/shop/{server_id}` - Boutique items
- `GET /api/economy/transactions/{server_id}` - Transactions
- `POST /api/economy/config/{server_id}` - Configuration

### Phase 3 : Modération
- `GET /api/moderation/warns/{server_id}` - Avertissements
- `GET /api/moderation/bans/{server_id}` - Bannissements
- `GET /api/moderation/logs/{server_id}` - Logs modération
- `POST /api/moderation/action/{server_id}` - Actions

### Phase 4 : Musique
- `GET /api/music/queue/{server_id}` - File d'attente
- `GET /api/music/history/{server_id}` - Historique
- `GET /api/music/status/{server_id}` - Statut lecteur
- `POST /api/music/control/{server_id}` - Contrôles

### Phase 5 : Gaming
- `GET /api/gaming/levels/{server_id}` - Niveaux utilisateurs
- `GET /api/gaming/rewards/{server_id}` - Récompenses
- `GET /api/gaming/leaderboard/{server_id}` - Classement
- `POST /api/gaming/xp/{server_id}` - Gestion XP

### Phase 6 : Analytics
- `GET /api/analytics/metrics/{server_id}` - Métriques serveur
- `GET /api/analytics/users/{server_id}` - Métriques utilisateurs
- `GET /api/analytics/events/{server_id}` - Événements
- `POST /api/analytics/report/{server_id}` - Génération rapports

## 💾 Base de Données

**Fichier** : `backend/arsenal_v4.db` (SQLite)

**Tables principales** :
- `economy_users`, `economy_shop_items`, `economy_transactions`
- `moderation_warns`, `moderation_bans`, `moderation_logs`
- `music_queue`, `music_history`, `music_playlists`
- `gaming_levels`, `gaming_rewards`, `gaming_stats`
- `analytics_server_metrics`, `analytics_user_metrics`, `analytics_events`

## 🔧 Configuration

### Variables d'environnement (optionnelles)
```bash
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/auth/callback
```

### Test de fonctionnement
```bash
cd backend
python test_final.py
```

## 🎊 Fonctionnalités

### ✅ Opérationnel
- **25+ APIs** avec données réelles
- **Base de données** complète avec +200 entrées
- **Interface React** avec 6 managers
- **Authentification** Discord OAuth
- **Permissions** hiérarchiques
- **Pas de simulation** - que du fonctionnel

### 🚧 En développement
- Interface utilisateur frontend complète
- Notifications en temps réel
- Export de données
- Thèmes personnalisés

## 🛠️ Résolution de problèmes

### Backend ne démarre pas
```bash
cd backend
pip install flask flask-cors requests sqlite3
python app.py
```

### Frontend ne démarre pas
```bash
# Installer Node.js depuis https://nodejs.org
cd frontend
npm install --force
npm start
```

### Base de données vide
```bash
cd backend
python create_tables.py
python populate_sample_data.py
```

## 📝 Logs

Les logs sont affichés dans les terminaux :
- **Backend** : Terminal Flask avec détails des requêtes
- **Frontend** : Terminal React avec hot-reload
- **Base de données** : Logs SQL dans la console

## 🎉 Support

Arsenal V4 WebPanel **Phase 6 COMPLÈTE** !
- ✅ 6 phases entièrement fonctionnelles
- ✅ Système de données réelles
- ✅ APIs complètes et testées
- ✅ Interface utilisateur opérationnelle

**Pas de simulation, que du réel !** 🔥
