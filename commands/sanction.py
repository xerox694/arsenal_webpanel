import discord
from discord import app_commands
import asyncio
from datetime import timedelta
from manager.sanctions_manager import add_sanction, sanctions
from core.logger import log

# 🔇 Mute vocal temporaire
@app_commands.command(name="mute", description="Mute vocal temporaire + ajout au casier")
@app_commands.describe(member="Membre à mute", durée="Durée en minutes")
async def mute(interaction: discord.Interaction, member: discord.Member, durée: int):
    if not member.voice or not member.voice.channel:
        await interaction.response.send_message("❌ Membre non connecté à un vocal.", ephemeral=True)
        return
    try:
        await member.edit(mute=True)
        await interaction.response.send_message(f"🔇 {member.mention} muté pendant {durée}min", ephemeral=True)
        add_sanction(member.id, "mute", "Mute vocal temporaire", str(interaction.user), durée=f"{durée}min", mode="slash")
        log.info(f"[MUTE] {member.display_name} → {durée}min")

        async def unmute_auto():
            await asyncio.sleep(durée * 60)
            try:
                await member.edit(mute=False)
                log.info(f"[UNMUTE] {member.display_name} rétabli")
            except Exception as e:
                log.warning(f"⚠️ Unmute échoué pour {member.display_name} → {e}")

        asyncio.create_task(unmute_auto())

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erreur : {e}", ephemeral=True)
        log.error(f"❌ Mute échoué {member.display_name} → {e}")

# ⏳ Timeout textuel
@app_commands.command(name="timeout", description="Timeout textuel avec casier")
@app_commands.describe(member="Membre à timeout", durée="Durée (ex: 10s, 10m, 10h, 10d)")
async def timeout(interaction: discord.Interaction, member: discord.Member, durée: str):
    try:
        unit = durée[-1].lower()
        value = int(durée[:-1])
        delta = {"s": timedelta(seconds=value), "m": timedelta(minutes=value), "h": timedelta(hours=value), "d": timedelta(days=value)}.get(unit)
        if not delta:
            await interaction.response.send_message("❌ Format invalide : s/m/h/d uniquement", ephemeral=True)
            return

        until = discord.utils.utcnow() + delta
        await member.timeout(until)
        await interaction.response.send_message(f"⏳ {member.mention} timeout pour {durée}", ephemeral=True)
        add_sanction(member.id, "timeout", "Sourdine textuelle", str(interaction.user), durée=durée, expiration=str(until), mode="slash")
        log.info(f"[TIMEOUT] {member.display_name} → {durée}")

    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erreur : {e}", ephemeral=True)
        log.error(f"❌ Timeout échoué {member.display_name} → {e}")

# 🔨 Ban définitif
@app_commands.command(name="ban", description="Bannit un membre du serveur")
@app_commands.describe(member="Membre à bannir", raison="Raison du ban")
async def ban(interaction: discord.Interaction, member: discord.Member, raison: str = "Non spécifiée"):
    try:
        await member.ban(reason=raison)
        await interaction.response.send_message(f"🔨 {member.display_name} banni. Raison : {raison}", ephemeral=True)
        add_sanction(member.id, "ban", raison, str(interaction.user), mode="slash")
        log.info(f"[BAN] {member.display_name} → {raison}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur ban : {e}", ephemeral=True)
        log.error(f"❌ Ban échoué {member.display_name} → {e}")

# 👢 Kick du serveur
@app_commands.command(name="kick", description="Expulse un membre du serveur")
@app_commands.describe(member="Membre à expulser", raison="Raison du kick")
async def kick(interaction: discord.Interaction, member: discord.Member, raison: str = "Non spécifiée"):
    try:
        await member.kick(reason=raison)
        await interaction.response.send_message(f"👢 {member.display_name} kické. Raison : {raison}", ephemeral=True)
        add_sanction(member.id, "kick", raison, str(interaction.user), mode="slash")
        log.info(f"[KICK] {member.display_name} → {raison}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur kick : {e}", ephemeral=True)
        log.error(f"❌ Kick échoué {member.display_name} → {e}")

# ⚠️ Avertissement simple
@app_commands.command(name="warn", description="Avertit un membre et ajoute au casier")
@app_commands.describe(member="Membre à avertir", raison="Raison de l'avertissement")
async def warn(interaction: discord.Interaction, member: discord.Member, raison: str = "Non spécifiée"):
    try:
        await interaction.response.send_message(f"⚠️ {member.mention} averti. Raison : {raison}", ephemeral=True)
        add_sanction(member.id, "warn", raison, str(interaction.user), mode="slash")
        log.info(f"[WARN] {member.display_name} → {raison}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur warn : {e}", ephemeral=True)
        log.error(f"❌ Warn échoué {member.display_name} → {e}")

# 🕊️ Unmute (bonus)
@app_commands.command(name="unmute", description="Rétablit un membre muté en vocal")
@app_commands.describe(member="Membre à unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.edit(mute=False)
        await interaction.response.send_message(f"🔈 {member.mention} n'est plus mute.", ephemeral=True)
        log.info(f"[UNMUTE MANUEL] {member.display_name} démuté")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur unmute : {e}", ephemeral=True)
        log.error(f"❌ Unmute échoué {member.display_name} → {e}")

# 🔓 UnTimeout (bonus)
@app_commands.command(name="untimeout", description="Retire le timeout d’un membre")
@app_commands.describe(member="Membre à réactiver")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.edit(timed_out_until=None)
        await interaction.response.send_message(f"⏱️ {member.mention} est rétabli.", ephemeral=True)
        log.info(f"[UNTIMEOUT] {member.display_name} retiré du timeout")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur untimeout : {e}", ephemeral=True)
        log.error(f"❌ Untimeout échoué {member.display_name} → {e}")

sanction_group = app_commands.Group(name="sanction", description="Commandes de sanction")

sanction_group.add_command(mute)
sanction_group.add_command(timeout)
sanction_group.add_command(ban)
sanction_group.add_command(kick)
sanction_group.add_command(warn)
sanction_group.add_command(unmute)
sanction_group.add_command(untimeout)