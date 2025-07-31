# Arsenal_V4 Web Panel - Guide de Test

## 🚀 Lancement du Web Panel

### 1. Installation des dépendances

**Backend (Python/Flask):**
```bash
cd webpanel/backend
pip install -r requirements.txt
```

**Frontend (React):**
```bash
cd webpanel/frontend
npm install
```

### 2. Lancement des serveurs

**Backend API (Terminal 1):**
```bash
cd webpanel/backend
python app.py
```
➡️ API accessible sur: http://localhost:5000

**Frontend React (Terminal 2):**
```bash
cd webpanel/frontend
npm start
```
➡️ Interface accessible sur: http://localhost:3000

### 3. Endpoints API disponibles

- `GET /` - Status de l'API
- `GET /api/status` - Status du bot et services
- `GET /api/stats` - Statistiques générales
- `GET /api/logs` - Logs récents

### 4. Test rapide

Une fois les deux serveurs lancés:
1. Ouvrir http://localhost:3000 dans votre navigateur
2. L'interface Arsenal_V4 devrait s'afficher
3. Vérifier que l'API répond sur http://localhost:5000

### 5. Scripts automatiques

Utilisez `start_webpanel.bat` pour lancer automatiquement les deux serveurs.
