import discord
from discord import app_commands
import os, sys, asyncio, json
from manager.config_manager import config_data, save_config
from core.logger import log

creator_group = app_commands.Group(name="creator", description="Commandes réservées au créateur d’Arsenal.")
CREATOR_ID = 431359112039890945  # Ton ID Discord ici
creator_tools_group = app_commands.Group(name="creator_tools", description="🔧 Outils avancés du créateur Arsenal")

def is_creator(user: discord.User) -> bool:
    return user.id == CREATOR_ID

# 🔄 Reload complet du bot
@creator_group.command(name="reload", description="Redémarre le bot proprement.")
async def reload(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé. Commande réservée au créateur.", ephemeral=True)
        return

    await interaction.response.send_message("♻️ Redémarrage du bot dans 3 secondes...", ephemeral=True)
    await asyncio.sleep(3)
    try:
        save_config()
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur reboot : {e}", ephemeral=True)

# 🔧 Modifier un paramètre global du bot
@creator_group.command(name="config_set", description="Modifie une clé dans config.json")
@app_commands.describe(cle="Nom du paramètre", valeur="Nouvelle valeur")
async def config_set(interaction: discord.Interaction, cle: str, valeur: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    config_data[cle] = valeur
    save_config()
    await interaction.response.send_message(f"✅ `{cle}` mis à jour → `{valeur}`", ephemeral=True)
    log.info(f"[CREATOR CONFIG] {cle} = {valeur}")

# 📄 Ajouter une note au changelog
@creator_group.command(name="add_changelog", description="Ajoute une entrée changelog à la version actuelle")
@app_commands.describe(note="Texte du changelog")
async def add_changelog(interaction: discord.Interaction, note: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    version = config_data.get("bot_version", "???")
    config_data.setdefault("changelog", {}).setdefault(version, []).append(note)
    save_config()
    await interaction.response.send_message(f"📝 Changelog ajouté à v{version}", ephemeral=True)
    log.info(f"[CREATOR CHANGELOG] + {note}")

# 🎯 Mettre à jour la version du bot
@creator_group.command(name="set_version", description="Change la version affichée du bot")
@app_commands.describe(version="Nouvelle version")
async def set_version(interaction: discord.Interaction, version: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    config_data["bot_version"] = version
    save_config()
    await interaction.response.send_message(f"📦 Version mise à jour → `{version}`", ephemeral=True)
    log.info(f"[CREATOR VERSION] → {version}")

# 🧠 Voir les bugs signalés (depuis bug_reports.json)
@creator_group.command(name="voir_bugs", description="Liste les bugs signalés dans bug_reports.json")
async def voir_bugs(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    try:
        with open("bug_reports.json", "r", encoding="utf-8") as f:
            bugs = json.load(f)

        if not bugs:
            await interaction.response.send_message("✅ Aucun bug signalé", ephemeral=True)
            return

        embed = discord.Embed(title="🐞 Bugs signalés", color=discord.Color.orange())
        for cmd, entries in bugs.items():
            for entry in entries[:3]:  # max 3 entrées par commande
                embed.add_field(
                    name=f"🧩 {cmd}",
                    value=f"• Par : {entry['user_name']}\n• Détails : {entry['details']}\n• Date : {entry['timestamp']}",
                    inline=False
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except FileNotFoundError:
        await interaction.response.send_message("❌ Aucun fichier bug_reports.json", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# 🎮 Status personnalisé
@creator_group.command(name="custom_status", description="Définit un statut personnalisé")
@app_commands.describe(status="Texte du statut")
async def custom_status(interaction: discord.Interaction, status: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    try:
        await interaction.client.change_presence(activity=discord.Game(name=status))
        await interaction.response.send_message(f"✅ Statut appliqué : `{status}`", ephemeral=True)
        log.info(f"[CREATOR STATUS] → {status}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# 🧪 Simuler un raid pour test sécurité
@creator_group.command(name="simulate_raid", description="Verrouille tous les salons (test sécurité)")
async def simulate_raid(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    guild = interaction.guild
    for c in guild.channels:
        perms = discord.PermissionOverwrite()
        if isinstance(c, discord.TextChannel):
            perms.send_messages = False
        elif isinstance(c, discord.VoiceChannel):
            perms.connect = False
        await c.set_permissions(guild.default_role, overwrite=perms)

    await interaction.response.send_message("🔒 Simu raid : salons verrouillés", ephemeral=True)

# 🔓 Reset sécurité après raid
@creator_group.command(name="reset_protection", description="Déverrouille tous les salons")
async def reset_protection(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    guild = interaction.guild
    for c in guild.channels:
        perms = discord.PermissionOverwrite()
        if isinstance(c, discord.TextChannel):
            perms.send_messages = True
        elif isinstance(c, discord.VoiceChannel):
            perms.connect = True
        await c.set_permissions(guild.default_role, overwrite=perms)

    await interaction.response.send_message("🔓 Protection réinitialisée", ephemeral=True)

# 🧪 SCAN du projet
@creator_group.command(name="scan", description="📁 Analyse le projet Arsenal")
async def scan(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    folders = ["manager", "commands", "modules", "data", "logs"]
    report = []

    for folder in folders:
        if not os.path.isdir(folder):
            report.append(f"❌ `{folder}` introuvable")
            continue

        files = os.listdir(folder)
        count = len(files)
        alert = "✅" if count else "⚠️"
        report.append(f"{alert} `{folder}` ➜ {count} fichier(s)")

    await interaction.response.send_message("🧪 Résultat scan :\n" + "\n".join(report), ephemeral=True)

# 📦 EXPORT config.json / projets
@creator_group.command(name="export_json", description="📤 Export config.json ou projects.json")
@app_commands.describe(filename="Nom du fichier à exporter")
async def export_json(interaction: discord.Interaction, filename: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    path = f"data/{filename}" if not filename.endswith(".json") else filename
    if not os.path.isfile(path):
        await interaction.response.send_message(f"❌ Fichier introuvable : `{path}`", ephemeral=True)
        return

    try:
        await interaction.response.send_message(
            content=f"📦 Export de `{filename}` :",
            file=discord.File(path),
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur export : {e}", ephemeral=True)

# 🛠️ PATCH config.json
@creator_group.command(name="patch_config", description="🛠️ Modifie une clé dans config.json")
@app_commands.describe(cle="Nom de la clé", valeur="Nouvelle valeur")
async def patch_config(interaction: discord.Interaction, cle: str, valeur: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    config_data[cle] = valeur
    save_config()
    await interaction.response.send_message(f"✅ `{cle}` patché avec succès : `{valeur}`", ephemeral=True)
    log.info(f"[PATCH] {cle} = {valeur}")

# 📋 LECTURE LOGS
@creator_group.command(name="logs", description="📋 Affiche les 10 dernières lignes de logs")
@app_commands.describe(file="Nom du fichier log (ex : arsenal_log.txt)")
async def logs(interaction: discord.Interaction, file: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    path = f"logs/{file}"
    if not os.path.isfile(path):
        await interaction.response.send_message(f"❌ Log introuvable : `{file}`", ephemeral=True)
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-10:]
        output = "\n".join(line.strip() for line in lines)
        await interaction.response.send_message(f"📄 Dernières lignes de `{file}` :\n```{output}```", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur lecture : {e}", ephemeral=True)

# 🔒 LOCKDOWN (serveur entier)
@creator_group.command(name="lockdown", description="🔒 Verrouille tous les salons (test sécurité)")
async def lockdown(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    guild = interaction.guild
    for c in guild.channels:
        perms = discord.PermissionOverwrite()
        if isinstance(c, discord.TextChannel):
            perms.send_messages = False
        elif isinstance(c, discord.VoiceChannel):
            perms.connect = False
        await c.set_permissions(guild.default_role, overwrite=perms)

    await interaction.response.send_message("🔐 Lockdown activé : salons verrouillés", ephemeral=True)

# 📥 PUSH V6 ➝ Serveur test
@creator_group.command(name="push_update", description="📥 Push manuel de la config vers serveurs tests")
async def push_update(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    config_data["last_push"] = str(discord.utils.utcnow())
    save_config()
    await interaction.response.send_message("📦 Configuration poussée vers serveurs de test. 🚀", ephemeral=True)
    log.info("[PUSH UPDATE] nouvelle config propagée")

# 📊 SYNC COUNT
@creator_group.command(name="sync_count", description="📊 Vérifie les commandes Slash enregistrées")
async def sync_count(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé", ephemeral=True)
        return

    try:
        cmds = interaction.client.tree.get_commands()
        total = len(cmds)
        names = [c.name for c in cmds]
        await interaction.response.send_message(f"📘 {total} commande(s) sync :\n`{', '.join(names)}`", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur sync check : {e}", ephemeral=True)

@app_commands.command(name="reset_bugs", description="🧹 Supprime tous les bugs signalés")
async def reset_bugs(interaction: discord.Interaction):
    if interaction.user.id != CREATOR_ID:
        await interaction.response.send_message("🚫 Réservé au créateur Arsenal", ephemeral=True)
        return

    try:
        path = "bug_reports.json"
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
            embed = discord.Embed(title="🧹 Bugs réinitialisés", description="Tous les signalements ont été effacés.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Le fichier bug_reports.json est introuvable", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)


# ⚙️ Register dans main.py
def setup(client: discord.Client):
    client.tree.add_command(creator_group)