import os

folders = [
    "webpanel",
    "webpanel/backend",
    "webpanel/backend/api",
    "webpanel/backend/config",
    "webpanel/backend/models",
    "webpanel/backend/utils",
    "webpanel/frontend",
    "webpanel/frontend/public",
    "webpanel/frontend/src",
    "webpanel/frontend/src/assets",
    "webpanel/frontend/src/assets/backgrounds",
    "webpanel/frontend/src/assets/icons",
    "webpanel/frontend/src/assets/fonts",
    "webpanel/frontend/src/components",
    "webpanel/frontend/src/components/common",
    "webpanel/frontend/src/contexts",
    "webpanel/frontend/src/hooks",
    "webpanel/frontend/src/services",
    "webpanel/frontend/src/styles"
]

files = {
    "webpanel/README.md": "# Arsenal_V4 Web Panel\n\nPanel web stylé et personnalisable pour Arsenal.",
    "webpanel/backend/app.py": "# Point d'entrée backend Flask/FastAPI\n",
    "webpanel/backend/api/routes.py": "# Routes API pour communication bot/panel\n",
    "webpanel/backend/config/config.py": "# Config backend\n",
    "webpanel/backend/models/user.py": "# Modèle utilisateur\n",
    "webpanel/backend/utils/security.py": "# Fonctions de sécurité\n",
    "webpanel/frontend/public/index.html": "<!-- Point d'entrée React/Vue -->\n",
    "webpanel/frontend/src/App.jsx": "// Point d'entrée principal React\n",
    "webpanel/frontend/src/index.js": "// Initialisation React\n",
    "webpanel/frontend/src/components/PanelDashboard.jsx": "// Dashboard principal\n",
    "webpanel/frontend/src/components/PanelSettings.jsx": "// Composant Settings\n",
    "webpanel/frontend/src/components/PanelAvatar.jsx": "// Composant Avatar IA\n",
    "webpanel/frontend/src/components/common/NeonButton.jsx": "// Bouton néon réutilisable\n",
    "webpanel/frontend/src/components/common/NeonCard.jsx": "// Carte néon réutilisable\n",
    "webpanel/frontend/src/contexts/PanelContext.jsx": "// Contexte global Panel\n",
    "webpanel/frontend/src/hooks/usePanelStatus.js": "// Hook custom Panel\n",
    "webpanel/frontend/src/services/api.js": "// Service API pour communication backend\n",
    "webpanel/frontend/src/styles/main.css": "/* Styles globaux néon/futuristes */\n"
}

base_path = os.path.dirname(__file__)

for folder in folders:
    os.makedirs(os.path.join(base_path, folder), exist_ok=True)

for path, content in files.items():
    full_path = os.path.join(base_path, path)
    if not os.path.exists(full_path):
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

print("✅ Architecture Web Panel Arsenal_V4 créée ! Tu peux personnaliser chaque fichier.")