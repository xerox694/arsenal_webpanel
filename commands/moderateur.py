import discord
from discord import app_commands
from core.logger import log

moderator_group = app_commands.Group(name="moderation", description="🛡️ Commandes de modération Arsenal")

@moderator_group.command(name="kick", description="Expulse un membre du serveur")
@app_commands.describe(user="Membre à expulser", reason="Raison du kick")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison"):
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"👢 {user.mention} expulsé.\n💬 Raison : {reason}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur lors du kick : {e}", ephemeral=True)

# NOTE: Les commandes ban et mute sont dans sanction.py pour éviter les doublons

@moderator_group.command(name="clear", description="🧹 Supprime les derniers messages d’un salon")
@app_commands.describe(amount="Nombre de messages à supprimer (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("❌ Tu dois choisir entre 1 et 100 messages.", ephemeral=True)
        return

    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 {len(deleted)} message(s) supprimé(s).")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur clear : {e}", ephemeral=True)

# 🔒 Mode anti-raid : verrouille tous les salons
@moderator_group.command(name="anti_raid", description="Verrouille tous les salons en cas de raid")
@app_commands.checks.has_permissions(administrator=True)
async def anti_raid(interaction: discord.Interaction):
    guild = interaction.guild
    for channel in guild.channels:
        perms = discord.PermissionOverwrite()
        if isinstance(channel, discord.TextChannel):
            perms.send_messages = False
        elif isinstance(channel, discord.VoiceChannel):
            perms.connect = False
        await channel.set_permissions(guild.default_role, overwrite=perms)
    await interaction.response.send_message("🔒 Tous les salons verrouillés", ephemeral=True)
    log.warning(f"[ANTI RAID] Activé sur {guild.name}")

# 🔓 Unlock all salons
@moderator_group.command(name="unlock_all", description="Déverrouille tous les salons")
@app_commands.checks.has_permissions(administrator=True)
async def unlock_all(interaction: discord.Interaction):
    guild = interaction.guild
    for channel in guild.channels:
        perms = discord.PermissionOverwrite()
        if isinstance(channel, discord.TextChannel):
            perms.send_messages = True
        elif isinstance(channel, discord.VoiceChannel):
            perms.connect = True
        await channel.set_permissions(guild.default_role, overwrite=perms)
    await interaction.response.send_message("🔓 Tous les salons déverrouillés", ephemeral=True)
    log.info(f"[UNLOCK] Tous les salons ouverts sur {guild.name}")

# 🧭 Stats serveur
@moderator_group.command(name="server_stats", description="Résumé de l’activité serveur")
async def server_stats(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 Stats — {guild.name}", color=discord.Color.blurple())
    embed.add_field(name="👥 Membres", value=guild.member_count)
    embed.add_field(name="📎 Rôles", value=len(guild.roles))
    embed.add_field(name="📚 Salons", value=len(guild.channels))
    embed.add_field(name="💎 Boosts", value=guild.premium_subscription_count)
    embed.add_field(name="🔥 Niveau", value=guild.premium_tier)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 📦 Move user vocal
@moderator_group.command(name="move_user", description="Déplace un utilisateur dans un salon vocal")
@app_commands.checks.has_permissions(move_members=True)
@app_commands.describe(member="Utilisateur", channel="Salon vocal cible")
async def move_user(interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if member.voice:
        await member.move_to(channel)
        await interaction.response.send_message(f"{member.mention} déplacé dans {channel.mention}", ephemeral=True)
        log.info(f"[MOVE] {member.display_name} → {channel.name}")
    else:
        await interaction.response.send_message("❌ Utilisateur pas en vocal", ephemeral=True)

# 🔧 Slowmode
@moderator_group.command(name="slowmode", description="Active un délai entre les messages")
@app_commands.describe(seconds="Délai en secondes")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"🕒 Slowmode activé : {seconds}s", ephemeral=True)

# 🧹 Clean channel
@moderator_group.command(name="clean_channel", description="Supprime tous les messages du salon")
@app_commands.checks.has_permissions(manage_messages=True)
async def clean_channel(interaction: discord.Interaction):
    deleted = await interaction.channel.purge()
    await interaction.response.send_message(f"{len(deleted)} messages supprimés", ephemeral=True)

# 🕵️ Analyse des rôles
@moderator_group.command(name="role_info", description="Infos sur un rôle")
@app_commands.describe(role="Rôle ciblé")
async def role_info(interaction: discord.Interaction, role: discord.Role):
    members = ", ".join(m.display_name for m in role.members)
    embed = discord.Embed(title=f"📛 Rôle : {role.name}", color=role.color)
    embed.add_field(name="Membres", value=members or "Aucun")
    embed.add_field(name="Couleur", value=str(role.color))
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 📢 Say public
@moderator_group.command(name="say", description="Envoie un embed public dans le salon")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(title="Titre", description="Message")
async def say(interaction: discord.Interaction, title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_footer(text=f"Par {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Message envoyé", ephemeral=True)

# 🔍 Check santé serveur
@moderator_group.command(name="check_health", description="Vérifie la configuration du serveur")
async def check_health(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🩺 Santé serveur : {guild.name}", color=discord.Color.green())
    embed.add_field(name="Membres", value=guild.member_count)
    embed.add_field(name="Vérification", value=guild.verification_level)
    embed.add_field(name="Boosts", value=guild.premium_subscription_count)
    embed.add_field(name="Niveau", value=guild.premium_tier)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 📥 Ajouter une dérogation (exemple ADC)
@moderator_group.command(name="ajouter_derogation", description="Ajoute une dérogation utilisateur")
@app_commands.describe(user_id="ID de l'utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def ajouter_derogation(interaction: discord.Interaction, user_id: int):
    from manager.ADC_manager import derogations
    if user_id not in derogations:
        derogations.append(user_id)
        await interaction.response.send_message(f"✅ Dérogation ajoutée pour `{user_id}`", ephemeral=True)
    else:
        await interaction.response.send_message(f"🚫 ID déjà dans la whitelist", ephemeral=True)

# 🗑️ Supprimer dérogation
@moderator_group.command(name="retirer_derogation", description="Retire une dérogation utilisateur")
@app_commands.describe(user_id="ID de l'utilisateur")
@app_commands.checks.has_permissions(administrator=True)
async def retirer_derogation(interaction: discord.Interaction, user_id: int):
    from manager.ADC_manager import derogations
    if user_id in derogations:
        derogations.remove(user_id)
        await interaction.response.send_message(f"✅ Dérogation retirée pour `{user_id}`", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ ID non présent dans la whitelist", ephemeral=True)

# 📜 Liste des dérogations
@moderator_group.command(name="liste_derogations", description="Liste des utilisateurs avec dérogation")
@app_commands.checks.has_permissions(administrator=True)
async def liste_derogations(interaction: discord.Interaction):
    from manager.ADC_manager import derogations
    if derogations:
        liste = ", ".join(str(uid) for uid in derogations)
        await interaction.response.send_message(f"📋 Dérogations actives : {liste}", ephemeral=True)
    else:
        await interaction.response.send_message("📭 Aucun utilisateur en dérogation", ephemeral=True)

# 🧠 Stats serveur vocal / messages
voice_time = {}
message_count = {}

@moderator_group.command(name="user_stats", description="Stats vocal & messages d’un utilisateur")
@app_commands.describe(member="Utilisateur")
async def user_stats(interaction: discord.Interaction, member: discord.Member):
    msg_count = message_count.get(member.id, 0)
    voice_duration = voice_time.get(member.id, 0)
    await interaction.response.send_message(
        f"🗂️ Stats pour {member.display_name}\n📨 Messages : {msg_count}\n🔊 Temps vocal : {int(voice_duration // 60)} min",
        ephemeral=True
    )

# 🧭 Analyse activité membres
@moderator_group.command(name="check_activity", description="Analyse des membres sans activité")
async def check_activity(interaction: discord.Interaction):
    inactive = [m.mention for m in interaction.guild.members if not m.activity and not m.bot]
    await interaction.response.send_message(f"🙈 Inactifs : {', '.join(inactive[:10])}...", ephemeral=True)

import discord
from discord import app_commands

moderator_group = app_commands.Group(name="mod", description="Commandes modération utilitaire")

# 🎛️ Lock text channel
@moderator_group.command(name="lock", description="Verrouille un salon texte")
@app_commands.describe(channel="Salon à verrouiller")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"🔒 {channel.mention} verrouillé.", ephemeral=True)

# 🔓 Unlock text channel
@moderator_group.command(name="unlock", description="Déverrouille un salon texte")
@app_commands.describe(channel="Salon à déverrouiller")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"🔓 {channel.mention} déverrouillé.", ephemeral=True)

# 🧽 Supprimer messages entre deux IDs
@moderator_group.command(name="sup_entre", description="Supprime tous les messages entre deux IDs")
@app_commands.describe(message_id1="ID de début", message_id2="ID de fin")
@app_commands.checks.has_permissions(manage_messages=True)
async def sup_entre(interaction: discord.Interaction, message_id1: int, message_id2: int):
    try:
        history = await interaction.channel.history(limit=1000).flatten()
        start, end = None, None
        for m in history:
            if m.id == message_id1:
                start = m
            if m.id == message_id2:
                end = m
        if start and end:
            to_delete = [msg for msg in history if start.created_at <= msg.created_at <= end.created_at]
            for msg in to_delete:
                await msg.delete()
            await interaction.response.send_message(f"✅ {len(to_delete)} messages supprimés", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Messages introuvables", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# 🛠️ Rename salon
@moderator_group.command(name="rename_channel", description="Renomme un salon texte")
@app_commands.describe(channel="Salon à renommer", new_name="Nouveau nom")
@app_commands.checks.has_permissions(manage_channels=True)
async def rename_channel(interaction: discord.Interaction, channel: discord.TextChannel, new_name: str):
    try:
        await channel.edit(name=new_name)
        await interaction.response.send_message(f"✅ Salon renommé en `{new_name}`", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# 🚫 Disable channel
@moderator_group.command(name="disable_channel", description="Empêche d’envoyer des messages dans un salon")
@app_commands.describe(channel="Salon à désactiver")
@app_commands.checks.has_permissions(manage_channels=True)
async def disable_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f"❌ Envoi désactivé dans `{channel.name}`", ephemeral=True)

# ✅ Enable channel
@moderator_group.command(name="enable_channel", description="Réautorise les messages dans un salon")
@app_commands.describe(channel="Salon à réactiver")
@app_commands.checks.has_permissions(manage_channels=True)
async def enable_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message(f"💬 Envoi réactivé dans `{channel.name}`", ephemeral=True)

# 🔄 Volume GUI (si ton bot joue un son)
@moderator_group.command(name="volume_gui", description="Régle le volume audio en %")
@app_commands.describe(volume="Volume entre 0 et 100")
async def volume_gui(interaction: discord.Interaction, volume: int):
    vc = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
    if not vc or not vc.is_playing():
        await interaction.response.send_message("❌ Aucun son en cours", ephemeral=True)
        return
    try:
        if not isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = volume / 100
        await interaction.response.send_message(f"🔊 Volume réglé à {volume}%", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)


# 📦 Setup groupe
def setup(client: discord.Client):
    client.tree.add_command(moderator_group)