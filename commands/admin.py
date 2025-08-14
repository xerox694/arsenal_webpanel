import discord
from discord import app_commands
import json
import os
from manager.config_manager import config_data, save_config, load_config
from core.logger import log

admin_group = app_commands.Group(name="admin", description="Commandes fondation serveur")

import subprocess
import threading

@admin_group.command(name="admingui", description="Ouvre le panel admin du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def admingui(interaction: discord.Interaction):
    await interaction.response.send_message("Ouverture du panel admin...", ephemeral=True)
    # Vérifie et installe les packages nécessaires
    try:
        import tkinter
    except ImportError:
        subprocess.run(["pip", "install", "tk"])
    # Lance le GUI admin en thread pour ne pas bloquer le bot
    from gui.ArsenalAdminGui import lancer_admin_interface
    def run_gui():
        user_id = interaction.user.id
        server_id = interaction.guild.id
        # Fonction pour récupérer les infos Discord (à adapter selon ton projet)
        def get_discord_data(server_id):
            guild = interaction.guild
            return {
                "name": guild.name,
                "owner": guild.owner.name if guild.owner else "Inconnu",
                "members": [{"id": m.id, "name": m.name, "main_role": m.top_role.name, "joined_at": str(m.joined_at)} for m in guild.members],
                "roles": [{"id": r.id, "name": r.name, "count": len(r.members)} for r in guild.roles],
                "created_at": str(guild.created_at)
            }
        lancer_admin_interface(user_id, server_id, get_discord_data)
    threading.Thread(target=run_gui).start()

# 💾 Sauvegarde serveur : rôles + salons
@admin_group.command(name="backup_server", description="Sauvegarde rôles + salons")
@app_commands.checks.has_permissions(administrator=True)
async def backup_server(interaction: discord.Interaction):
    guild = interaction.guild
    backup = {
        "server_name": guild.name,
        "roles": [{role.name: role.permissions.value} for role in guild.roles],
        "channels": [channel.name for channel in guild.channels]
    }

    path = f"data/{guild.id}_backup.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(backup, f, indent=4)

    await interaction.response.send_message("✅ Sauvegarde serveur effectuée avec succès.", ephemeral=True)
    log.info(f"[BACKUP] {guild.name} → {path}")

# 📁 Restaurer configuration serveur
@admin_group.command(name="load_backup", description="Restaure une configuration depuis un fichier backup")
@app_commands.describe(filename="Nom du fichier JSON à charger")
@app_commands.checks.has_permissions(administrator=True)
async def load_backup(interaction: discord.Interaction, filename: str):
    path = f"data/{filename}"
    if not os.path.exists(path):
        await interaction.response.send_message("❌ Fichier introuvable.", ephemeral=True)
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            backup = json.load(f)

        for role_data in backup["roles"]:
            for name, perms in role_data.items():
                await interaction.guild.create_role(name=name, permissions=discord.Permissions(perms))

        for ch_name in backup["channels"]:
            await interaction.guild.create_text_channel(name=ch_name)

        await interaction.response.send_message("✅ Restauration terminée.", ephemeral=True)
        log.info(f"[RESTORE] {filename} chargé dans {interaction.guild.name}")

    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)
        log.error(f"[RESTORE ERROR] {filename} → {e}")

@admin_group.command(name="activer_communautaire", description="Active le mode communautaire sur ce serveur.")
@app_commands.checks.has_permissions(administrator=True)
async def activer_communautaire(interaction: discord.Interaction):
    try:
        await interaction.guild.edit(features=[
            "COMMUNITY",
            "WELCOME_SCREEN_ENABLED",
            "MEMBER_VERIFICATION_GATE_ENABLED",
            "NEWS"
        ])
        await interaction.response.send_message("✅ Mode communautaire activé.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Permission insuffisante.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erreur : {e}", ephemeral=True)

server_rules_channels = {}
server_rules = {}

@admin_group.command(name="set_rules_channel", description="Définit le canal dédié au règlement.")
@app_commands.checks.has_permissions(administrator=True)
async def set_rules_channel(interaction: discord.Interaction):
    server_rules_channels[interaction.guild.id] = interaction.channel.id
    await interaction.response.send_message("✅ Ce canal servira au règlement.", ephemeral=True)

@admin_group.command(name="add_rule", description="Ajoute une règle.")
@app_commands.describe(rule="Texte de la règle")
@app_commands.checks.has_permissions(administrator=True)
async def add_rule(interaction: discord.Interaction, rule: str):
    rules = server_rules.setdefault(interaction.guild.id, [])
    rules.append(rule)
    await interaction.response.send_message(f"✅ Règle ajoutée : {rule}", ephemeral=True)

@admin_group.command(name="remove_rule", description="Supprime une règle.")
@app_commands.describe(index="Numéro de la règle")
@app_commands.checks.has_permissions(administrator=True)
async def remove_rule(interaction: discord.Interaction, index: int):
    rules = server_rules.get(interaction.guild.id, [])
    if 0 < index <= len(rules):
        removed = rules.pop(index - 1)
        await interaction.response.send_message(f"✅ Règle supprimée : {removed}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Index invalide.", ephemeral=True)

@admin_group.command(name="publish_rules", description="Envoie le règlement dans le canal dédié.")
@app_commands.checks.has_permissions(administrator=True)
async def publish_rules(interaction: discord.Interaction):
    sid = interaction.guild.id
    cid = server_rules_channels.get(sid)
    rules = server_rules.get(sid, [])
    channel = interaction.guild.get_channel(cid)

    if not channel or not rules:
        await interaction.response.send_message("❌ Impossible de publier. Vérifie la config.", ephemeral=True)
        return

    embed = discord.Embed(title="📜 Règlement du serveur", color=discord.Color.blue())
    for i, rule in enumerate(rules, 1):
        embed.add_field(name=f"Règle {i}", value=rule, inline=False)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Règlement publié.", ephemeral=True)

@admin_group.command(name="reset_rules", description="Réinitialise les règles du serveur.")
@app_commands.checks.has_permissions(administrator=True)
async def reset_rules(interaction: discord.Interaction):
    server_rules[interaction.guild.id] = []
    await interaction.response.send_message("✅ Règlement réinitialisé.", ephemeral=True)

@admin_group.command(name="list_boosters", description="Liste les membres qui boostent le serveur.")
async def list_boosters(interaction: discord.Interaction):
    boosters = interaction.guild.premium_subscribers
    booster_names = ", ".join([booster.mention for booster in boosters])
    message = f"**Boosters du serveur** : {booster_names if boosters else 'Aucun'}"
    await interaction.response.send_message(message, ephemeral=True)

@admin_group.command(name="verify_links", description="Analyse les liens postés et identifie ceux qui pourraient être suspects.")
@app_commands.describe(message_id="ID du message à analyser")
async def verify_links(interaction: discord.Interaction, message_id: int):
    try:
        msg = await interaction.channel.fetch_message(message_id)
        links = [word for word in msg.content.split() if word.startswith("http")]
        flagged = [l for l in links if not l.startswith("https")]
        if flagged:
            await interaction.response.send_message(f"⚠️ Liens suspects : {', '.join(flagged)}", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Aucun lien suspect détecté.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)