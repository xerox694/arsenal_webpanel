import discord
import json, os, asyncio
from core.logger import log

HUB_CONFIG_PATH = "hub_config.json"

async def restore_voice_channels(client: discord.Client):
    if not os.path.exists(HUB_CONFIG_PATH):
        log.warning("🧠 Aucun fichier hub_config.json détecté pour restaurer les vocaux.")
        return

    try:
        with open(HUB_CONFIG_PATH, "r", encoding="utf-8") as f:
            hubs = json.load(f)
    except Exception as e:
        log.error(f"[RESTORE] Erreur lecture hub_config : {e}")
        return

    client.temporary_voice_channels = {}

    for hub_id, data in hubs.items():
        owner_id = data.get("owner_id")
        main_channel_id = data.get("main_channel_id")
        category_id = data.get("category_id")

        guilds = client.guilds
        for guild in guilds:
            channel = guild.get_channel(main_channel_id)
            if not channel:
                log.warning(f"[RESTORE] Salon principal introuvable : {main_channel_id}")
                continue

            # Ajouter au cache
            client.temporary_voice_channels[str(hub_id)] = channel
            log.info(f"[RESTORE] Hub vocal restauré : {channel.name}")

async def suppress_expired_channels(client: discord.Client):
    """
    Supprime les salons vocaux temporaires qui ne sont plus utilisés depuis X temps.
    (à appeler périodiquement via task loop)
    """
    to_remove = []
    for hub_id, channel in getattr(client, "temporary_voice_channels", {}).items():
        if isinstance(channel, discord.VoiceChannel) and not channel.members:
            to_remove.append(hub_id)

    for hub_id in to_remove:
        channel = client.temporary_voice_channels.get(hub_id)
        try:
            await channel.delete()
            log.info(f"[VOCAL] Salon {channel.name} supprimé (inactif)")
            del client.temporary_voice_channels[hub_id]
        except Exception as e:
            log.error(f"[VOCAL] Erreur suppression {channel.name} ➜ {e}")

def setup_voice_manager(client: discord.Client):
    loop = asyncio.get_event_loop()
    loop.create_task(restore_voice_channels(client))

    async def loop_suppression():
        while True:
            await suppress_expired_channels(client)
            await asyncio.sleep(3)  # toutes les 15 minutes

    loop.create_task(loop_suppression())