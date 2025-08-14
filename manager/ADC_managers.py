import discord
from core.logger import log

derogations = []


import os

def whitelist_ids():
    """
    Récupère tous les IDs Discord whitelistés à partir des variables .env.
    Exemples valides dans .env :
    - ADC_USER1=123456789012345678
    - XeroX_ALPHA=987654321098765432
    """
    ids = []
    for key, val in os.environ.items():
        if key.startswith("ADC_") or key.startswith("XeroX_"):
            try:
                ids.append(int(val))
            except ValueError:
                continue
    return ids

def is_whitelisted(user_id: int) -> bool:
    """
    Vérifie si l'utilisateur est présent dans la whitelist ADC
    """
    return user_id in whitelist_ids()

def afficher_whitelist_console():
    """
    Affiche tous les IDs whitelistés dans la console
    """
    ids = whitelist_ids()
    print(f"🔐 Whitelist ADC - {len(ids)} ID(s) détectés :")
    for i, uid in enumerate(ids, 1):
        print(f"{i}. {uid}")

def ajouter_adc_env(nom: str, discord_id: int):
    """
    Ajoute une entrée ADC dans le .env runtime (⚠️ temporaire si non persisté)
    """
    try:
        os.environ[nom] = str(discord_id)
        print(f"✅ Ajouté : {nom} = {discord_id}")
    except Exception as e:
        print(f"❌ Erreur ajout env : {e}")

async def on_member_join(member):
    guild = member.guild
    suspected = {}

    for other in guild.members:
        if other.id != member.id and other.name == member.name:
            suspected.setdefault(other.name, []).append(other)

    if suspected.get(member.name) and member.id not in derogations:
        try:
            await member.kick(reason="Double compte détecté (sans dérogation)")
            await guild.system_channel.send(f"🛡️ {member.mention} a été kické automatiquement.")
            log.info(f"👤 Kick auto : doublon détecté pour {member.name}")
        except discord.Forbidden:
            await guild.system_channel.send("❌ Impossible de kick (permissions)")
            log.warning(f"⚠️ Kick refusé pour {member.name} (permissions)")
    else:
        await guild.system_channel.send(f"{member.mention} a rejoint sans doublon.")
        log.info(f"👤 Nouveau membre : {member.name}")