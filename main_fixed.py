# 🌐 Discord + environnement
import discord
from discord.ext import commands, tasks
import asyncio, os, sys, json, datetime
from dotenv import load_dotenv

# 🧠 Core config & logs
from core.logger import log
from manager.config_manager import config_data, load_config, save_config

# 🔄 Système de rechargement de modules (NOUVEAU)
try:
    from core.module_reloader import ReloaderCommands
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

# 🛡️ Système AutoMod Ultra-Avancé (NOUVEAU)
try:
    from modules.automod_system import AutoModCog, automod_group
    AUTOMOD_AVAILABLE = True
    print("✅ Système AutoMod Ultra-Avancé chargé")
except Exception as e:
    AUTOMOD_AVAILABLE = False
    print(f"⚠️ Système AutoMod non disponible: {e}")

# 🎧 Système Voice Hub Ultra-Avancé (NOUVEAU)
try:
    from modules.voice_hub_system import VoiceHubCog, voice_hub_group, voice_control_group
    VOICE_HUB_AVAILABLE = True
    print("✅ Système Voice Hub Ultra-Avancé chargé")
except Exception as e:
    VOICE_HUB_AVAILABLE = False
    print(f"⚠️ Système Voice Hub non disponible: {e}")

# 📡 Managers système & extension
from manager.voice_manager import restore_voice_channels
from manager.terminal_manager import start_terminal
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

# 🛠️ Panneau Creator GUI (Tkinter)
from gui.ArsenalCreatorStudio import lancer_creator_interface

# 🔐 Modules ADC / autres
# from manager.ADC_managers import whitelist_ids  # Décommente si utilisé

# 📥 Modules supplémentaires (à ajouter si présents)
# from manager.feedback_manager import get_bug_data
# from manager.giveaway_manager import launch_giveaway
# from modules.message_tracker import log_message

load_dotenv()

# Configuration bot
PREFIX = config_data.get("PREFIX", "!")
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

# ⚡ Fonction de changement de statut
async def cycle_status(bot):
    while not bot.is_ready():
        await asyncio.sleep(1)
    while True:
        stats = [
            discord.Activity(type=discord.ActivityType.streaming, name=f"{sum(bot.command_usage.values())} commandes utilisées", url="https://twitch.tv/xerox"),
            discord.Activity(type=discord.ActivityType.playing, name="Arsenal Admin Studio 2025"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} serveurs"),
        ]
        for act in stats:
            await bot.change_presence(activity=act)
            await asyncio.sleep(10)

class ArsenalBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        
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
        
        # 🛡️ Charger le système AutoMod
        if AUTOMOD_AVAILABLE:
            try:
                await self.add_cog(AutoModCog(self))
                log.info("✅ Système AutoMod Ultra-Avancé chargé")
            except Exception as e:
                log.error(f"❌ Erreur chargement AutoMod: {e}")
        
        # 🎧 Charger le système Voice Hub
        if VOICE_HUB_AVAILABLE:
            try:
                await self.add_cog(VoiceHubCog(self))
                log.info("✅ Système Voice Hub Ultra-Avancé chargé")
            except Exception as e:
                log.error(f"❌ Erreur chargement Voice Hub: {e}")

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

# 🛡️ AutoMod Commands (NOUVEAU)
if AUTOMOD_AVAILABLE:
    client.tree.add_command(automod_group)

# 🎧 Voice Hub Commands (NOUVEAU)
if VOICE_HUB_AVAILABLE:
    client.tree.add_command(voice_hub_group)
    client.tree.add_command(voice_control_group)

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

# 🏹 Hunt Royal Profiles Commands (NOUVEAU)
if HUNT_PROFILES_AVAILABLE:
    client.tree.add_command(hunt_profiles.setup_hunt_profile)
    client.tree.add_command(hunt_profiles.view_hunt_profile)
    client.tree.add_command(hunt_profiles.update_hunt_stats)

# Démarrer le bot avec gestion des erreurs de token
if TOKEN:
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        log.error("❌ TOKEN Discord invalide ! Vérifiez votre fichier .env")
        print("❌ TOKEN Discord invalide ! Vérifiez votre fichier .env")
    except Exception as e:
        log.error(f"❌ Erreur lors du démarrage du bot: {e}")
        print(f"❌ Erreur lors du démarrage du bot: {e}")
else:
    log.error("❌ Aucun TOKEN Discord trouvé ! Créez un fichier .env avec DISCORD_TOKEN=votre_token")
    print("❌ Aucun TOKEN Discord trouvé ! Créez un fichier .env avec DISCORD_TOKEN=votre_token")
