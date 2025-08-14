#!/usr/bin/env python3
# 🚀 Arsenal WebPanel V5 - Script de Lancement

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Affiche le banner Arsenal V5"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                 🚀 ARSENAL WEBPANEL V5 🚀                    ║
    ║                                                              ║
    ║             Interface Web Moderne pour Arsenal               ║
    ║                                                              ║
    ║  • Sidebar Exceptionnelle    • Gestion des Serveurs         ║
    ║  • 120+ Commandes           • Interface Temps Réel          ║
    ║  • Design Moderne           • Authentification Sécurisée    ║
    ║                                                              ║
    ║                   Développé par XeRoX                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur est requis")
        return False
    print(f"✅ Python {sys.version.split()[0]} détecté")
    return True

def check_dependencies():
    """Vérifie et installe les dépendances"""
    print("\n🔍 Vérification des dépendances...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("❌ Fichier requirements.txt introuvable")
        return False
    
    try:
        # Vérifier si les dépendances sont installées
        import flask
        import flask_cors
        import flask_socketio
        print("✅ Dépendances principales détectées")
        return True
    except ImportError:
        print("⚠️  Installation des dépendances...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("✅ Dépendances installées avec succès")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances")
            return False

def setup_environment():
    """Configure l'environnement"""
    print("\n⚙️  Configuration de l'environnement...")
    
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  Création du fichier .env...")
        env_template = """# Arsenal V5 WebPanel Configuration
WEBPANEL_SECRET_KEY=your_secret_key_here
CREATOR_ID=431359112039890945
FLASK_ENV=development
PORT=5000
DEBUG=true

# Discord OAuth (À configurer)
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/auth/callback
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Fichier .env créé - Veuillez le configurer")
    else:
        print("✅ Fichier .env existant")

def check_port_availability(port):
    """Vérifie si le port est disponible"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
        return True
    except OSError:
        return False

def start_webpanel():
    """Démarre le WebPanel"""
    print("\n🚀 Démarrage d'Arsenal WebPanel V5...")
    
    # Définir le port
    port = int(os.environ.get('PORT', 5000))
    
    # Vérifier la disponibilité du port
    if not check_port_availability(port):
        print(f"⚠️  Port {port} occupé, tentative sur le port {port + 1}")
        port += 1
        if not check_port_availability(port):
            print(f"❌ Ports {port-1} et {port} occupés")
            return False
    
    print(f"🌐 Port sélectionné: {port}")
    print(f"📱 URL locale: http://localhost:{port}")
    print("🔄 Démarrage du serveur...")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter\n")
    
    # Définir les variables d'environnement
    os.environ['PORT'] = str(port)
    
    try:
        # Importer et démarrer l'app
        from app import app, socketio
        
        # Démarrer avec SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('FLASK_ENV') == 'development',
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Arsenal WebPanel V5 arrêté par l'utilisateur")
        return True
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")
        return False

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifications préalables
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    setup_environment()
    
    # Charger les variables d'environnement
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Variables d'environnement chargées")
    except Exception as e:
        print(f"⚠️  Erreur chargement .env: {e}")
    
    # Démarrer le WebPanel
    if not start_webpanel():
        sys.exit(1)

if __name__ == "__main__":
    main()
