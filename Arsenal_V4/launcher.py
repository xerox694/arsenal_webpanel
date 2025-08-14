#!/usr/bin/env python3
"""
🤖 Arsenal V4 - Lanceur Principal
=================================

Script de démarrage principal pour le bot Arsenal V4
"""

import os
import sys
import asyncio
import signal
import logging
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire du bot au path
bot_dir = Path(__file__).parent / "bot"
sys.path.insert(0, str(bot_dir))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arsenal_v4.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('Arsenal.Launcher')

class ArsenalLauncher:
    """Lanceur principal pour Arsenal V4"""
    
    def __init__(self):
        self.bot = None
        self.start_time = None
        self.running = False
        
    def print_banner(self):
        """Afficher le banner Arsenal V4"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      🤖 Arsenal V4 - Bot Discord Révolutionnaire 🤖          ║
║                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                               ║
║  💰 Économie complète avec ArsenalCoins                      ║
║  🎮 Mini-jeux avec roulette, slots, quiz                     ║
║  🛒 Boutique configurable avec inventaires                   ║
║  🛡️  Modération intelligente et auto-modération              ║
║  🎵 Système de musique YouTube intégré                       ║
║  📊 Statistiques et analytics avancés                        ║
║  🎨 Personnalisation complète des profils                    ║
║  ⚙️  Administration et monitoring système                     ║
║                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                               ║
║  🚀 "Ouvrir une porte vers une ère nouvelle avec le bot"     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕒 Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 67)
        print()
    
    def check_requirements(self):
        """Vérifier les prérequis de démarrage"""
        logger.info("🔍 Vérification des prérequis...")
        
        # Vérifier Python version
        if sys.version_info < (3, 10):
            logger.error(f"❌ Python 3.10+ requis (trouvé: {sys.version})")
            return False
        
        logger.info(f"✅ Python {sys.version.split()[0]}")
        
        # Vérifier les fichiers essentiels
        required_files = [
            "bot/main.py",
            "bot/database.py",
            "bot/modules/__init__.py"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logger.error(f"❌ Fichier manquant: {file_path}")
                return False
        
        logger.info("✅ Fichiers essentiels présents")
        
        # Vérifier les variables d'environnement
        discord_token = os.getenv('DISCORD_TOKEN')
        if not discord_token:
            logger.error("❌ Variable DISCORD_TOKEN manquante !")
            logger.error("📝 Créez un fichier .env avec votre token Discord")
            return False
        
        logger.info("✅ Token Discord configuré")
        
        # Vérifier les dépendances
        try:
            import discord
            logger.info(f"✅ Discord.py {discord.__version__}")
        except ImportError:
            logger.error("❌ Discord.py non installé !")
            logger.error("📦 Exécutez: pip install -r requirements.txt")
            return False
        
        return True
    
    def setup_signal_handlers(self):
        """Configurer les gestionnaires de signaux"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Signal {signum} reçu, arrêt en cours...")
            self.shutdown()
        
        # Gérer les signaux d'arrêt
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        else:
            signal.signal(signal.SIGINT, signal_handler)
    
    def load_environment(self):
        """Charger les variables d'environnement"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("✅ Variables d'environnement chargées")
        except ImportError:
            logger.warning("⚠️ python-dotenv non disponible, variables système utilisées")
    
    async def start_bot(self):
        """Démarrer le bot"""
        try:
            # Importer le bot
            from main import ArsenalBot
            
            # Créer l'instance
            self.bot = ArsenalBot()
            self.start_time = datetime.now()
            self.running = True
            
            logger.info("🤖 Démarrage du bot Arsenal V4...")
            
            # Démarrer le bot
            discord_token = os.getenv('DISCORD_TOKEN')
            await self.bot.start(discord_token)
            
        except KeyboardInterrupt:
            logger.info("⚠️ Interruption clavier détectée")
            await self.shutdown()
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}")
            await self.shutdown()
    
    async def shutdown(self):
        """Arrêter proprement le bot"""
        if self.running:
            logger.info("🛑 Arrêt du bot en cours...")
            self.running = False
            
            if self.bot and not self.bot.is_closed():
                await self.bot.close()
            
            if self.start_time:
                uptime = datetime.now() - self.start_time
                logger.info(f"⏱️ Uptime: {uptime}")
            
            logger.info("✅ Bot arrêté proprement")
    
    def create_directories(self):
        """Créer les répertoires nécessaires"""
        directories = [
            "logs",
            "backups",
            "data",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info("📁 Répertoires créés/vérifiés")
    
    async def run(self):
        """Lancer le bot Arsenal V4"""
        try:
            # Affichage initial
            self.print_banner()
            
            # Vérifications
            if not self.check_requirements():
                return 1
            
            # Configuration
            self.load_environment()
            self.setup_signal_handlers()
            self.create_directories()
            
            logger.info("🚀 Lancement d'Arsenal V4...")
            print()
            
            # Démarrer le bot
            await self.start_bot()
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Erreur de lancement: {e}")
            return 1

def main():
    """Point d'entrée principal"""
    launcher = ArsenalLauncher()
    
    try:
        # Exécuter le launcher
        if sys.platform == "win32":
            # Windows
            return asyncio.run(launcher.run())
        else:
            # Unix/Linux
            return asyncio.run(launcher.run())
    
    except KeyboardInterrupt:
        print("\n⚠️ Arrêt forcé par l'utilisateur")
        return 130
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    # Changer vers le répertoire du script
    os.chdir(Path(__file__).parent)
    
    # Lancer
    exit_code = main()
    sys.exit(exit_code)
