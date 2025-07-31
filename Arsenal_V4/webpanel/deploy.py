"""
🌐 Script de Déploiement Public Arsenal V4 WebPanel
Configuration pour l'hébergement en ligne
"""
import os
import sys
import subprocess
import json
from pathlib import Path

class ArsenalDeployment:
    def __init__(self):
        self.project_path = Path(__file__).parent
        self.config = {
            "host": "0.0.0.0",  # Écoute sur toutes les interfaces
            "port": 5000,       # Port standard pour production
            "debug": False,     # Désactivé en production
            "domain": None,     # Sera configuré
            "ssl": False        # À activer avec certificat
        }
    
    def check_requirements(self):
        """Vérifier les prérequis pour le déploiement"""
        print("🔍 Vérification des prérequis...")
        
        required_files = [
            "backend/advanced_server.py",
            "backend/sqlite_database.py",
            "advanced_interface.html",
            "login.html"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_path / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Fichiers manquants: {missing_files}")
            return False
        
        print("✅ Tous les fichiers requis sont présents")
        return True
    
    def create_deployment_config(self):
        """Créer la configuration de déploiement"""
        print("⚙️ Création de la configuration de déploiement...")
        
        # Configuration Flask pour production
        production_config = {
            "SECRET_KEY": os.urandom(24).hex(),
            "DATABASE_URL": "sqlite:///arsenal_v4_production.db",
            "CORS_ORIGINS": ["*"],  # À configurer selon vos besoins
            "SESSION_TIMEOUT": 86400,  # 24 heures
            "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16MB max
            "DISCORD_CLIENT_ID": "VOTRE_CLIENT_ID",
            "DISCORD_CLIENT_SECRET": "VOTRE_CLIENT_SECRET",
            "DISCORD_REDIRECT_URI": "http://votre-domaine.com/auth/callback",
            "BOT_TOKEN": "VOTRE_BOT_TOKEN"
        }
        
        config_file = self.project_path / "production_config.json"
        with open(config_file, 'w') as f:
            json.dump(production_config, f, indent=4)
        
        print(f"✅ Configuration sauvegardée: {config_file}")
        return production_config
    
    def create_wsgi_file(self):
        """Créer le fichier WSGI pour déploiement"""
        print("📄 Création du fichier WSGI...")
        
        wsgi_content = '''#!/usr/bin/env python3
"""
🚀 WSGI Entry Point pour Arsenal V4 WebPanel
Configuration de production pour serveurs web
"""
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
project_path = Path(__file__).parent
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(project_path / "backend"))

# Charger la configuration de production
import json
config_file = project_path / "production_config.json"
if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
    
    # Définir les variables d'environnement
    for key, value in config.items():
        os.environ[key] = str(value)

# Importer l'application
from backend.advanced_server import create_app
application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
'''
        
        wsgi_file = self.project_path / "wsgi.py"
        with open(wsgi_file, 'w', encoding='utf-8') as f:
            f.write(wsgi_content)
        
        print(f"✅ Fichier WSGI créé: {wsgi_file}")
    
    def create_requirements_txt(self):
        """Créer requirements.txt pour le déploiement"""
        print("📦 Création du fichier requirements.txt...")
        
        requirements = [
            "Flask==2.3.3",
            "Flask-CORS==4.0.0",
            "requests==2.31.0",
            "python-dotenv==1.0.0",
            "gunicorn==21.2.0",  # Serveur WSGI pour production
            "discord.py==2.3.2",
            "aiohttp==3.8.5",
            "cryptography==41.0.4",
            "Werkzeug==2.3.7"
        ]
        
        req_file = self.project_path / "requirements.txt"
        with open(req_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        print(f"✅ Requirements créé: {req_file}")
    
    def create_dockerfile(self):
        """Créer un Dockerfile pour conteneurisation"""
        print("🐳 Création du Dockerfile...")
        
        dockerfile_content = '''# Arsenal V4 WebPanel Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' arsenal && \\
    chown -R arsenal:arsenal /app
USER arsenal

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
'''
        
        dockerfile = self.project_path / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"✅ Dockerfile créé: {dockerfile}")
    
    def create_docker_compose(self):
        """Créer docker-compose.yml"""
        print("🐳 Création du docker-compose.yml...")
        
        compose_content = '''version: '3.8'

services:
  arsenal-webpanel:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - arsenal-webpanel
    restart: unless-stopped

volumes:
  data:
  logs:
'''
        
        compose_file = self.project_path / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        print(f"✅ Docker Compose créé: {compose_file}")
    
    def create_nginx_config(self):
        """Créer la configuration Nginx"""
        print("🌐 Création de la configuration Nginx...")
        
        nginx_content = '''events {
    worker_connections 1024;
}

http {
    upstream arsenal {
        server arsenal-webpanel:5000;
    }
    
    server {
        listen 80;
        server_name votre-domaine.com;  # À modifier
        
        # Redirection HTTPS (optionnel)
        # return 301 https://$server_name$request_uri;
        
        location / {
            proxy_pass http://arsenal;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Servir les fichiers statiques directement
        location /static {
            alias /app/static;
            expires 7d;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Configuration HTTPS (décommentez si vous avez un certificat SSL)
    # server {
    #     listen 443 ssl;
    #     server_name votre-domaine.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     location / {
    #         proxy_pass http://arsenal;
    #         proxy_set_header Host $host;
    #         proxy_set_header X-Real-IP $remote_addr;
    #         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #         proxy_set_header X-Forwarded-Proto $scheme;
    #     }
    # }
}
'''
        
        nginx_file = self.project_path / "nginx.conf"
        with open(nginx_file, 'w') as f:
            f.write(nginx_content)
        
        print(f"✅ Configuration Nginx créée: {nginx_file}")
    
    def create_deployment_scripts(self):
        """Créer les scripts de déploiement"""
        print("📜 Création des scripts de déploiement...")
        
        # Script de déploiement simple
        deploy_script = '''#!/bin/bash
# Script de deploiement Arsenal V4 WebPanel

echo "Deploiement Arsenal V4 WebPanel..."

# Arreter les conteneurs existants
docker-compose down

# Construire et demarrer
docker-compose up --build -d

echo "Deploiement termine!"
echo "Panel accessible sur: http://localhost"

# Afficher les logs
docker-compose logs -f
'''
        
        deploy_file = self.project_path / "deploy.sh"
        with open(deploy_file, 'w', encoding='utf-8') as f:
            f.write(deploy_script)
        
        # Script Windows
        deploy_bat = '''@echo off
echo Deploiement Arsenal V4 WebPanel...

docker-compose down
docker-compose up --build -d

echo Deploiement termine!
echo Panel accessible sur: http://localhost

docker-compose logs -f
'''
        
        deploy_bat_file = self.project_path / "deploy.bat"
        with open(deploy_bat_file, 'w') as f:
            f.write(deploy_bat)
        
        print(f"✅ Scripts de déploiement créés")
    
    def create_env_template(self):
        """Créer un template .env"""
        print("🔧 Création du template .env...")
        
        env_content = '''# Arsenal V4 WebPanel - Configuration Environnement
# Copiez ce fichier vers .env et remplissez les valeurs

# Configuration Discord
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_REDIRECT_URI=http://votre-domaine.com/auth/callback

# Configuration Flask
SECRET_KEY=your_secret_key_here
FLASK_ENV=production

# Base de données
DATABASE_URL=sqlite:///arsenal_v4.db

# Sécurité
SESSION_TIMEOUT=86400
MAX_CONTENT_LENGTH=16777216

# Domaine
DOMAIN=votre-domaine.com
SSL_ENABLED=false

# CORS
CORS_ORIGINS=*
'''
        
        env_file = self.project_path / ".env.template"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Template .env créé: {env_file}")
    
    def deploy(self):
        """Lancer le processus de déploiement complet"""
        print("🚀 === DÉPLOIEMENT ARSENAL V4 WEBPANEL ===")
        print()
        
        if not self.check_requirements():
            print("❌ Prérequis non satisfaits. Arrêt du déploiement.")
            return False
        
        try:
            self.create_deployment_config()
            self.create_wsgi_file()
            self.create_requirements_txt()
            self.create_dockerfile()
            self.create_docker_compose()
            self.create_nginx_config()
            self.create_deployment_scripts()
            self.create_env_template()
            
            print()
            print("✅ === DÉPLOIEMENT PRÉPARÉ AVEC SUCCÈS ===")
            print()
            print("📋 PROCHAINES ÉTAPES:")
            print("1. Configurez votre .env à partir du template")
            print("2. Modifiez nginx.conf avec votre domaine")
            print("3. Exécutez: ./deploy.sh (Linux/Mac) ou deploy.bat (Windows)")
            print("4. Configurez votre DNS pour pointer vers votre serveur")
            print("5. Optionnel: Ajoutez un certificat SSL")
            print()
            print("🌐 MÉTHODES DE DÉPLOIEMENT DISPONIBLES:")
            print("• Docker (recommandé): docker-compose up")
            print("• Serveur local: python wsgi.py")
            print("• Gunicorn: gunicorn wsgi:application")
            print("• Apache/Nginx: Utilisez wsgi.py comme point d'entrée")
            print()
            print(f"📁 Tous les fichiers créés dans: {self.project_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du déploiement: {e}")
            return False

# Point d'entrée
if __name__ == "__main__":
    deployer = ArsenalDeployment()
    deployer.deploy()
