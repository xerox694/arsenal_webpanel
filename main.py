# 🌐 Discord + environnement
import discord
from discord.ext import commands, tasks
import asyncio, os, sys, json, datetime
from dotenv import load_dotenv

# 🧠 Core config & logs
from core.logger import log
from manager.config_manager import config_data, load_config, save_config

# � Système de rechargement de modules (NOUVEAU)
try:
    from core.module_reloader import ReloaderCommands, reload_group
    RELOADER_AVAILABLE = True
    print("✅ Système de rechargement de modules chargé")
except Exception as e:
    RELOADER_AVAILABLE = False
    print(f"⚠️ Système de rechargement non disponible: {e}")

# 🏹 Modules Hunt Royal et Suggestions (NOUVEAU)
try:
    from modules.hunt_royal_system import HuntRoyalCommands
    from modules.suggestions_system import SuggestionsCommands
    HUNT_ROYAL_AVAILABLE = True
    SUGGESTIONS_AVAILABLE = True
    print("✅ Modules Hunt Royal et Suggestions chargés")
except Exception as e:
    HUNT_ROYAL_AVAILABLE = False
    SUGGESTIONS_AVAILABLE = False
    print(f"⚠️ Modules Hunt Royal/Suggestions non disponibles: {e}")

# �🔌 Managers système & extension
from manager.voice_manager import restore_voice_channels
from manager.terminal_manager import start_terminal
# from manager.economy_manager import balances  # Décommente si utilisé
from manager.memory_manager import memoire    # pour les stats, exceptions

# 🎧 Setup audio
from commands.music import setup_audio

# 💬 Modules de commandes
import commands.creator_tools as creator
import commands.community as community
import commands.admin as admin
import commands.moderateur as moderateur
import commands.sanction as sanction
import commands.music as music

# 🏹 Hunt Royal Auth System (NOUVEAU)
try:
    import commands.hunt_royal_auth as hunt_auth
    HUNT_AUTH_AVAILABLE = True
    print("✅ Hunt Royal Auth System chargé")
except Exception as e:
    HUNT_AUTH_AVAILABLE = False
    print(f"⚠️ Hunt Royal Auth non disponible: {e}")

# 🏹 Hunt Royal Profiles System (NOUVEAU)
try:
    import commands.hunt_royal_profiles as hunt_profiles
    HUNT_PROFILES_AVAILABLE = True
    print("✅ Hunt Royal Profiles System chargé")
except Exception as e:
    HUNT_PROFILES_AVAILABLE = False
    print(f"⚠️ Hunt Royal Profiles non disponible: {e}")

# 🛠️ Panneau Creator GUI (Tkinter)
from gui.ArsenalCreatorStudio import lancer_creator_interface

# 🔐 Modules ADC / autres
# from manager.ADC_managers import whitelist_ids  # Décommente si utilisé

# 📥 Modules supplémentaires (à ajouter si présents)
# from manager.feedback_manager import get_bug_data
# from manager.giveaway_manager import launch_giveaway
# from modules.message_tracker import log_message



load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_ID = int(os.getenv("CREATOR_ID", 431359112039890945))
PREFIX = os.getenv("PREFIX", "!")

# Vérification du token Discord
print("🔍 Vérification des variables d'environnement...")
print(f"TOKEN présent: {'✅ Oui' if TOKEN else '❌ NON'}")
print(f"CREATOR_ID: {CREATOR_ID}")
print(f"PREFIX: {PREFIX}")

if not TOKEN:
    print("❌ ERREUR CRITIQUE: DISCORD_TOKEN manquant dans les variables d'environnement!")
    print("📋 Ajoutez DISCORD_TOKEN sur Render avec votre token de bot Discord")
    sys.exit(1)

intents = discord.Intents.all()

from discord import Activity, ActivityType, Streaming

async def cycle_status(bot):
    while not bot.is_ready():
        await asyncio.sleep(1)
    while True:
        stats = [
            Streaming(name="Arsenal Admin Studio", url="https://twitch.tv/xerox"),
            Activity(type=ActivityType.streaming, name=f"{sum(bot.command_usage.values())} commandes utilisées", url="https://twitch.tv/xerox"),
            Activity(type=ActivityType.watching, name=f"{len(os.listdir('.'))} dossiers, {sum(len(files) for _, _, files in os.walk('.'))} fichiers"),
            Activity(type=ActivityType.watching, name=f"{len(bot.guilds)} serveurs"),
            Activity(type=ActivityType.playing, name="Developed by XeRoX"),
        ]
        for act in stats:
            await bot.change_presence(activity=act)
            await asyncio.sleep(15)

class ArsenalBot(commands.Bot):
    async def setup_hook(self):
        # Ajoute ici les tâches de fond à lancer au démarrage
        self.loop.create_task(restore_voice_channels(self))
        self.loop.create_task(start_terminal(self))
        self.loop.create_task(cycle_status(self))
        setup_audio(self)
        
        # 🔄 Charger le système de rechargement de modules
        if RELOADER_AVAILABLE:
            try:
                await self.add_cog(ReloaderCommands(self))
                log.info("✅ Système de rechargement de modules chargé")
            except Exception as e:
                log.error(f"❌ Erreur chargement reloader: {e}")
        
        # 🏹 Charger Hunt Royal et Suggestions
        if HUNT_ROYAL_AVAILABLE:
            try:
                await self.add_cog(HuntRoyalCommands(self))
                log.info("✅ Module Hunt Royal chargé")
            except Exception as e:
                log.error(f"❌ Erreur chargement Hunt Royal: {e}")
        
        if SUGGESTIONS_AVAILABLE:
            try:
                await self.add_cog(SuggestionsCommands(self))
                log.info("✅ Module Suggestions chargé")
            except Exception as e:
                log.error(f"❌ Erreur chargement Suggestions: {e}")

client = ArsenalBot(command_prefix=PREFIX, intents=intents)
client.startup_time = datetime.datetime.utcnow()
client.command_usage = {}

@client.event
async def on_ready():
    streaming = discord.Streaming(
        name="Arsenal Admin Studio",
        url="https://www.twitch.tv/fakestream"
    )
    await client.change_presence(activity=streaming, status=discord.Status.online)
    print(f"{client.user} est prêt et en streaming !")
    log.info(f"[START] Arsenal Studio lancé comme {client.user.name}")
    try:
        await client.tree.sync()
        log.info(f"[SYNC] Commandes Slash synchronisées.")
        # Démarre le cycle de status ici
        if not hasattr(client, "status_task"):
            client.status_task = asyncio.create_task(cycle_status(client))
    except Exception as e:
        log.error(f"[SYNC ERROR] {e}")

# 📥 Imports modules
client.tree.add_command(moderateur.moderator_group)
client.tree.add_command(admin.admin_group)
client.tree.add_command(creator.creator_group)
client.tree.add_command(sanction.sanction_group)
client.tree.add_command(creator.creator_tools_group)

# 📘 Individuelles
client.tree.add_command(community.info)
client.tree.add_command(community.avatar)
client.tree.add_command(community.signaler_bug)
client.tree.add_command(community.vote)
client.tree.add_command(community.poll)
client.tree.add_command(community.magic_8ball)
client.tree.add_command(community.spin_wheel)
client.tree.add_command(community.top_vocal)
client.tree.add_command(community.top_messages)
client.tree.add_command(community.random_quote)
client.tree.add_command(community.leaderboard)
client.tree.add_command(community.version)

# 🏹 Hunt Royal Auth Commands (NOUVEAU)
if HUNT_AUTH_AVAILABLE:
    client.tree.add_command(hunt_auth.register_hunt_royal)
    client.tree.add_command(hunt_auth.get_my_token)
    client.tree.add_command(hunt_auth.hunt_royal_stats)

# 🏹 Hunt Royal Profile Commands (NOUVEAU)
if HUNT_PROFILES_AVAILABLE:
    client.tree.add_command(hunt_profiles.link_hunt_royal)
    client.tree.add_command(hunt_profiles.profile_hunt_royal)
    client.tree.add_command(hunt_profiles.unlink_hunt_royal)

# Ajoute ici les autres commandes individuelles si besoin

# � Reload System Commands (NOUVEAU)
if RELOADER_AVAILABLE:
    client.tree.add_command(reload_group)

# �👑 Creator GUI Panel
def lancer_gui():
    try:
        lancer_creator_interface(client)
    except Exception as e:
        log.warning(f"[GUI ERROR] {e}")

# 🚀 Lancement
if __name__ == "__main__":
    import threading
    threading.Thread(target=lancer_gui, daemon=True).start()
    try:
        client.run(TOKEN)
    except Exception as e:
        log.error(f"[RUN ERROR] {e}")
