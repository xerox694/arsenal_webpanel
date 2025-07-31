import os
import json
import discord
import asyncio
from core.logger import log

HUB_CONFIG_PATH = "data/hub_config.json"
temporary_voice_channels = {}

def load_hub_config():
    if os.path.exists(HUB_CONFIG_PATH):
        try:
            with open(HUB_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                log.info("📦 hub_config.json chargé")
                return data
        except Exception as e:
            log.error(f"❌ Erreur chargement hub config : {e}")
    return {}

def save_hub_config(data):
    try:
        with open(HUB_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            log.info("💾 hub_config.json sauvegardé")
    except Exception as e:
        log.error(f"⚠️ Erreur sauvegarde hub config : {e}")

async def restore_voice_channels(client):
    config = load_hub_config()
    for hub_id, infos in config.items():
        try:
            guild = discord.utils.get(client.guilds, id=infos["guild_id"])
            main_channel = guild.get_channel(infos["main_channel_id"])
            category_channel = guild.get_channel(infos["category_id"])

            if not guild or not main_channel or not category_channel:
                raise ValueError("💥 Guild / channel manquant")

            temporary_voice_channels[int(hub_id)] = {
                "main_channel": main_channel,
                "temporary_channels": {},
                "category": category_channel,
                "owner_id": infos.get("owner_id"),
                "moderators_ids": infos.get("moderators_ids", {}),
                "whitelist_ids": infos.get("whitelist_ids", []),
                "config_visible_roles": infos.get("config_visible_roles", ["Admin"]),
                "discussion_channel": guild.get_channel(infos.get("discussion_channel_id", 0))
            }

            log.info(f"✅ Hub vocal restauré : {main_channel.name} ({guild.name})")

        except Exception as e:
            log.warning(f"⚠️ Échec restauration hub {hub_id} → {e}")