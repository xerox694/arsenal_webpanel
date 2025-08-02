#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL V4 - SCRIPT DE PRÉPARATION DÉPLOIEMENT
Prépare tous les fichiers nécessaires pour le déploiement sur Render
"""

import os
import json
import subprocess
import shutil
from pathlib import Path

class RenderDeployPrep:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.required_files = [
            'main.py',
            'webpanel_advanced.py', 
            'requirements.txt',
            'render.yaml',
            'core/',
            'modules/',
            'commands/',
            'utils/',
            'templates/',
            'static/',
            'data/',
            'logs/'
        ]
        
    def check_files(self):
        """Vérifie que tous les fichiers nécessaires sont présents"""
        print("🔍 Vérification des fichiers requis...")
        missing_files = []
        
        for file_path in self.required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"❌ Manquant: {file_path}")
            else:
                print(f"✅ Trouvé: {file_path}")
        
        if missing_files:
            print(f"\n⚠️ {len(missing_files)} fichier(s) manquant(s) détecté(s)")
            return False
        
        print("✅ Tous les fichiers requis sont présents")
        return True
    
    def create_directories(self):
        """Crée les répertoires nécessaires"""
        print("\n📁 Création des répertoires...")
        
        directories = ['data', 'logs', 'static', 'templates']
        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Répertoire créé: {directory}")
            
            # Créer .gitkeep pour les répertoires vides
            gitkeep = dir_path / '.gitkeep'
            if not gitkeep.exists():
                gitkeep.touch()
    
    def update_requirements(self):
        """Met à jour requirements.txt avec toutes les dépendances"""
        print("\n📦 Mise à jour requirements.txt...")
        
        requirements = [
            "discord.py==2.3.2",
            "Flask==2.3.3",
            "Flask-CORS==4.0.0", 
            "Flask-SocketIO==5.3.6",
            "python-socketio[client]==5.8.0",
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "gunicorn==21.2.0",
            "psutil==5.9.5",
            "aiohttp==3.9.5",
            "Pillow>=10.3.0",
            "beautifulsoup4==4.12.2",
            "asyncio",
            "json5",
            "colorama",
            "python-dateutil"
        ]
        
        req_file = self.root_dir / 'requirements.txt'
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
        
        print("✅ requirements.txt mis à jour")
    
    def create_env_template(self):
        """Crée un template des variables d'environnement"""
        print("\n🔧 Création du template .env...")
        
        env_template = """# 🔑 VARIABLES D'ENVIRONNEMENT ARSENAL V4
# ============================================

# 🤖 Configuration Discord (OBLIGATOIRE)
DISCORD_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here  
DISCORD_CLIENT_SECRET=your_client_secret_here

# ⚙️ Configuration Bot
BOT_PREFIX=!
DEBUG=false

# 🌐 Configuration WebPanel
FLASK_ENV=production
WEB_SECRET_KEY=your_secret_key_here
WEB_AUTH_ENABLED=true

# 🚀 Configuration Render
ARSENAL_MODE=production
MAX_LOG_LINES=1000
AUTO_RESTART=true
PORT=10000

# 📊 Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO"""

        env_file = self.root_dir / '.env.template'
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        
        print("✅ Template .env créé")
    
    def create_gitignore(self):
        """Crée/met à jour .gitignore"""
        print("\n📋 Configuration .gitignore...")
        
        gitignore_content = """# Fichiers de configuration sensibles
.env
*.db
*.sqlite3
arsenal_v4.db
hunt_royal*.db
suggestions.db

# Logs et cache
logs/*.log
*.log
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.cache/

# Données temporaires
data/temp/
data/cache/
hunt_royal_cache.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
$RECYCLE.BIN/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# Test coverage
htmlcov/
.coverage
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Spyder
.spyderproject
.spyproject"""

        gitignore_file = self.root_dir / '.gitignore'
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("✅ .gitignore configuré")
    
    def create_procfile(self):
        """Crée Procfile pour Heroku (optionnel)"""
        print("\n⚙️ Création Procfile...")
        
        procfile_content = "web: python webpanel_advanced.py --start-bot --host=0.0.0.0 --port=$PORT --production"
        
        procfile = self.root_dir / 'Procfile'
        with open(procfile, 'w', encoding='utf-8') as f:
            f.write(procfile_content)
        
        print("✅ Procfile créé")
    
    def update_webpanel_for_production(self):
        """Met à jour webpanel_advanced.py pour la production"""
        print("\n🔧 Configuration production webpanel...")
        
        webpanel_file = self.root_dir / 'webpanel_advanced.py'
        if not webpanel_file.exists():
            print("❌ webpanel_advanced.py introuvable")
            return
        
        # Lire le contenu actuel
        with open(webpanel_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # S'assurer que le mode production est supporté
        if '--production' not in content:
            production_code = '''
        # Mode production pour Render/Heroku
        parser.add_argument('--production', action='store_true', 
                          help='Mode production (désactive debug, optimise performances)')'''
            
            if 'argparse' in content and 'add_argument' in content:
                # Ajouter l'argument production
                content = content.replace(
                    'parser.add_argument(\'--port\'',
                    f'{production_code}\n        parser.add_argument(\'--port\''
                )
        
        # Sauvegarder
        with open(webpanel_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ WebPanel configuré pour la production")
    
    def create_deployment_script(self):
        """Crée un script de déploiement automatique"""
        print("\n🚀 Création script de déploiement...")
        
        deploy_script = '''#!/bin/bash
# 🚀 Script de déploiement Arsenal V4 sur Render

echo "🚀 Arsenal V4 - Déploiement Render"
echo "=================================="

# Vérification Git
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

# Vérification des fichiers
echo "🔍 Vérification des fichiers..."
python prepare_render_deploy.py

if [ $? -ne 0 ]; then
    echo "❌ Vérification échouée"
    exit 1
fi

# Initialisation Git si nécessaire
if [ ! -d ".git" ]; then
    echo "📦 Initialisation du repository Git..."
    git init
    git branch -M main
fi

# Ajouter tous les fichiers
echo "📁 Ajout des fichiers..."
git add .

# Commit
echo "💾 Commit des changements..."
git commit -m "🚀 Arsenal V4 - Configuration complète pour Render"

# Configuration remote (à modifier avec votre URL)
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Configuration remote GitHub..."
    echo "⚠️  Configurez votre remote GitHub:"
    echo "   git remote add origin https://github.com/USERNAME/REPO.git"
    echo "   git push -u origin main"
else
    echo "📤 Push vers GitHub..."
    git push origin main
fi

echo ""
echo "✅ Préparation terminée !"
echo ""
echo "🌐 Étapes suivantes:"
echo "1. Aller sur render.com"
echo "2. Connecter votre repository GitHub" 
echo "3. Configurer les variables d'environnement"
echo "4. Déployer !"
echo ""
echo "📖 Documentation complète: DEPLOY_RENDER_GUIDE.md"'''

        deploy_file = self.root_dir / 'deploy.sh'
        with open(deploy_file, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        # Rendre exécutable sur Unix
        try:
            os.chmod(deploy_file, 0o755)
        except:
            pass
        
        print("✅ Script deploy.sh créé")
    
    def run_preparation(self):
        """Lance toute la préparation"""
        print("🚀 Arsenal V4 - Préparation Déploiement Render")
        print("=" * 50)
        
        # Étapes de préparation
        steps = [
            ("Vérification fichiers", self.check_files),
            ("Création répertoires", self.create_directories),
            ("Mise à jour requirements", self.update_requirements),
            ("Template environnement", self.create_env_template),
            ("Configuration .gitignore", self.create_gitignore),
            ("Création Procfile", self.create_procfile),
            ("Configuration production", self.update_webpanel_for_production),
            ("Script déploiement", self.create_deployment_script)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            try:
                step_func()
                success_count += 1
            except Exception as e:
                print(f"❌ Erreur {step_name}: {e}")
        
        print(f"\n🎉 Préparation terminée: {success_count}/{len(steps)} étapes réussies")
        
        if success_count == len(steps):
            print("\n✅ Prêt pour le déploiement !")
            print("\n📋 Prochaines étapes:")
            print("1. Configurer les variables d'environnement dans .env.template")
            print("2. Exécuter: ./deploy.sh (ou git add . && git commit && git push)")
            print("3. Configurer sur render.com")
            print("\n📖 Guide complet: DEPLOY_RENDER_GUIDE.md")
        else:
            print("\n⚠️ Certaines étapes ont échoué, vérifiez les erreurs ci-dessus")

if __name__ == "__main__":
    prep = RenderDeployPrep()
    prep.run_preparation()
