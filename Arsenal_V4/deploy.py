#!/usr/bin/env python3
"""
🚀 Arsenal V4 - Script de Déploiement Automatique
================================================

Ce script automatise le déploiement du bot Arsenal V4 sur Render
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class ArsenalDeployer:
    """Déployeur automatique pour Arsenal V4"""
    
    def __init__(self):
        self.project_name = "Arsenal V4"
        self.version = "4.0.0"
        self.start_time = datetime.now()
        
    def print_header(self):
        """Afficher l'en-tête du déploiement"""
        print("=" * 60)
        print(f"🚀 {self.project_name} - Déploiement Automatique")
        print(f"📦 Version: {self.version}")
        print(f"🕒 Démarré: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
    
    def check_requirements(self):
        """Vérifier les prérequis"""
        print("🔍 Vérification des prérequis...")
        
        # Vérifier Git
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print("✅ Git installé")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git non trouvé ! Veuillez installer Git.")
            return False
        
        # Vérifier Python
        if sys.version_info < (3, 10):
            print(f"❌ Python 3.10+ requis (trouvé: {sys.version})")
            return False
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Vérifier les fichiers essentiels
        required_files = [
            "bot/main.py",
            "requirements.txt",
            "render.yaml"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Fichier manquant: {file}")
                return False
        print("✅ Fichiers essentiels présents")
        
        return True
    
    def prepare_environment(self):
        """Préparer l'environnement de déploiement"""
        print("\n📋 Préparation de l'environnement...")
        
        # Créer le fichier .env d'exemple s'il n'existe pas
        env_example = """# Arsenal V4 Bot - Variables d'environnement
# ============================================

# Token Discord (OBLIGATOIRE)
DISCORD_TOKEN=votre_token_discord_ici

# Base de données
DATABASE_URL=./arsenal_v4.db

# Environnement (development/production)
ENVIRONMENT=production

# Debug (true/false)
DEBUG=false

# Port pour le WebPanel (optionnel)
PORT=10000
"""
        
        if not os.path.exists(".env.example"):
            with open(".env.example", "w", encoding="utf-8") as f:
                f.write(env_example)
            print("✅ Fichier .env.example créé")
        
        # Vérifier .gitignore
        gitignore_content = """# Arsenal V4 - Gitignore
# ======================

# Environnement
.env
.venv/
venv/
env/

# Base de données
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Cache Python
__pycache__/
*.pyc
*.pyo
*.pyd
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

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup
backups/
*.backup

# Temp files
temp/
tmp/
*.tmp
"""
        
        if not os.path.exists(".gitignore"):
            with open(".gitignore", "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            print("✅ Fichier .gitignore créé")
        
        return True
    
    def install_dependencies(self):
        """Installer les dépendances"""
        print("\n📦 Installation des dépendances...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print("✅ Dépendances installées")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation: {e}")
            return False
    
    def run_tests(self):
        """Exécuter les tests de base"""
        print("\n🧪 Tests de base...")
        
        # Test d'import des modules
        try:
            sys.path.append("bot")
            
            # Test d'import du bot principal
            import importlib.util
            spec = importlib.util.spec_from_file_location("main", "bot/main.py")
            if spec and spec.loader:
                print("✅ Module principal importable")
            else:
                print("❌ Erreur import module principal")
                return False
            
            # Test de la structure de la base de données
            if os.path.exists("bot/database.py"):
                spec = importlib.util.spec_from_file_location("database", "bot/database.py")
                if spec and spec.loader:
                    print("✅ Module base de données importable")
                else:
                    print("❌ Erreur import base de données")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur tests: {e}")
            return False
    
    def git_operations(self):
        """Opérations Git"""
        print("\n📤 Opérations Git...")
        
        try:
            # Vérifier si on est dans un repo Git
            subprocess.run(["git", "status"], check=True, capture_output=True)
            
            # Ajouter tous les fichiers
            subprocess.run(["git", "add", "."], check=True)
            print("✅ Fichiers ajoutés au staging")
            
            # Commit
            commit_message = f"🚀 Deploy Arsenal V4 {self.version} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
            print("✅ Commit créé")
            
            # Push
            subprocess.run(["git", "push"], check=True)
            print("✅ Push vers le repository")
            
            return True
            
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in str(e):
                print("ℹ️ Aucun changement à commiter")
                return True
            print(f"❌ Erreur Git: {e}")
            return False
    
    def generate_deployment_info(self):
        """Générer les informations de déploiement"""
        print("\n📋 Génération des informations de déploiement...")
        
        deployment_info = {
            "project": self.project_name,
            "version": self.version,
            "deployment_time": self.start_time.isoformat(),
            "python_version": sys.version,
            "requirements": [],
            "structure": {},
            "render_config": {
                "build_command": "pip install -r requirements.txt",
                "start_command": "python bot/main.py",
                "environment": "python",
                "plan": "starter"
            }
        }
        
        # Lire les requirements
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r", encoding="utf-8") as f:
                deployment_info["requirements"] = [
                    line.strip() for line in f.readlines() 
                    if line.strip() and not line.startswith("#")
                ]
        
        # Structure des fichiers
        for root, dirs, files in os.walk("."):
            # Ignorer certains dossiers
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc'):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    deployment_info["structure"][rel_path] = {
                        "size": os.path.getsize(os.path.join(root, file)),
                        "modified": datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(root, file))
                        ).isoformat()
                    }
        
        # Sauvegarder
        with open("deployment_info.json", "w", encoding="utf-8") as f:
            json.dump(deployment_info, f, indent=2, ensure_ascii=False)
        
        print("✅ Informations de déploiement sauvegardées")
        return True
    
    def print_deployment_instructions(self):
        """Afficher les instructions de déploiement"""
        print("\n" + "=" * 60)
        print("🎉 PRÉPARATION TERMINÉE !")
        print("=" * 60)
        print()
        print("📋 INSTRUCTIONS POUR RENDER:")
        print()
        print("1. 🌐 Allez sur https://render.com")
        print("2. ➕ Créez un nouveau service 'Worker'")
        print("3. 🔗 Connectez votre repository GitHub")
        print("4. ⚙️ Configuration:")
        print("   • Build Command: pip install -r requirements.txt")
        print("   • Start Command: python bot/main.py")
        print("   • Environment: python")
        print("   • Plan: Starter (ou Free)")
        print()
        print("5. 🔑 Variables d'environnement OBLIGATOIRES:")
        print("   • DISCORD_TOKEN: votre_token_discord")
        print("   • ENVIRONMENT: production")
        print("   • DEBUG: false")
        print()
        print("6. 🚀 Cliquez sur 'Deploy'")
        print()
        print("=" * 60)
        print("📚 DOCUMENTATION:")
        print("• README.md - Guide complet")
        print("• deployment_info.json - Infos détaillées")
        print("• .env.example - Variables d'environnement")
        print()
        print("🆘 SUPPORT:")
        print("• Issues GitHub pour les bugs")
        print("• Wiki pour la documentation")
        print("=" * 60)
    
    def deploy(self):
        """Processus de déploiement complet"""
        self.print_header()
        
        # Étapes de déploiement
        steps = [
            ("Vérification des prérequis", self.check_requirements),
            ("Préparation de l'environnement", self.prepare_environment),
            ("Installation des dépendances", self.install_dependencies),
            ("Tests de base", self.run_tests),
            ("Opérations Git", self.git_operations),
            ("Génération des infos de déploiement", self.generate_deployment_info)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"\n❌ ÉCHEC: {step_name}")
                print("🛑 Déploiement arrêté")
                return False
        
        self.print_deployment_instructions()
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        print(f"\n⏱️ Durée totale: {duration.total_seconds():.2f} secondes")
        print(f"🎯 Déploiement préparé avec succès !")
        
        return True

def main():
    """Point d'entrée principal"""
    deployer = ArsenalDeployer()
    
    try:
        success = deployer.deploy()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Déploiement interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
