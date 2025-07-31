import discord
from discord import app_commands
import json, random
from manager.config_manager import config_data
from manager.economy_manager import balances
from manager.sanctions_manager import sanctions
from manager.memory_manager import memoire

# 📘 /info
@app_commands.command(name="info", description="Affiche des informations sur le bot Arsenal")
async def info(interaction: discord.Interaction):
    bot_name = interaction.client.user.name
    guild_count = len(interaction.client.guilds)
    version = interaction.client.volume if hasattr(interaction.client, "volume") else "?"
    embed = discord.Embed(title="📘 Arsenal Admin Studio", color=discord.Color.green())
    embed.add_field(name="🤖 Nom du bot", value=bot_name, inline=True)
    embed.add_field(name="🖥️ Serveurs actifs", value=str(guild_count), inline=True)
    embed.add_field(name="⚙️ Version", value=version, inline=True)
    embed.set_footer(text="Propulsé par Arsenal Admin Studio")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# 🖼️ /avatar
@app_commands.command(name="avatar", description="Affiche l'avatar d’un utilisateur")
@app_commands.describe(user="Utilisateur ciblé")
async def avatar(interaction: discord.Interaction, user: discord.User):
    url = user.display_avatar.url
    embed = discord.Embed(title=f"Avatar de {user.name}", color=discord.Color.blurple())
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 🟢 /ping
@app_commands.command(name="ping", description="Vérifie si le bot est actif")
async def ping(interaction: discord.Interaction):
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong ! Latence : {latency} ms", ephemeral=True)

# ✨ /style
@app_commands.command(name="style", description="Change le style de réponse du bot")
@app_commands.describe(tone="Style : amical, sérieux ou humoristique")
async def style(interaction: discord.Interaction, tone: str):
    tones = {
        "amical": "Salut 😊 Comment puis-je t’aider aujourd’hui ?",
        "sérieux": "Bonjour. Que puis-je faire pour vous ?",
        "humoristique": "Oh un humain ? Qu’est-ce que je peux concocter pour toi ? 😄"
    }
    answer = tones.get(tone.lower())
    if answer:
        await interaction.response.send_message(answer, ephemeral=True)
    else:
        await interaction.response.send_message("❌ Style inconnu. Choisis : amical, sérieux ou humoristique.", ephemeral=True)

# 📊 /poll — Crée un sondage multi-options
@app_commands.command(name="poll", description="Crée un sondage")
@app_commands.describe(question="Question du sondage", options="Options séparées par des virgules")
async def poll(interaction: discord.Interaction, question: str, options: str):
    choices = options.split(",")
    if len(choices) < 2 or len(choices) > 5:
        await interaction.response.send_message("❌ Entre 2 et 5 options uniquement", ephemeral=True)
        return

    embed = discord.Embed(title="📊 Sondage", description=question, color=discord.Color.blue())
    emojis = ["🇦", "🇧", "🇨", "🇩", "🇪"]
    for emoji, option in zip(emojis, choices):
        embed.add_field(name=emoji, value=option.strip(), inline=False)

    message = await interaction.channel.send(embed=embed)
    for emoji in emojis[:len(choices)]:
        await message.add_reaction(emoji)

    await interaction.response.send_message("✅ Sondage créé avec succès", ephemeral=True)

# 👍 /vote — Vote simple oui/non
@app_commands.command(name="vote", description="Lance un vote rapide")
@app_commands.describe(question="Question à poser")
async def vote(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="🗳️ Vote", description=question, color=discord.Color.green())
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    await interaction.response.send_message("✅ Vote lancé", ephemeral=True)

# 📬 /report — Signale un membre à l’administration
@app_commands.command(name="report", description="Signale un membre à l'administration")
@app_commands.describe(member="Membre à signaler", reason="Raison du signalement")
async def report(interaction: discord.Interaction, member: discord.Member, reason: str):
    channel_id = config_data.get("admin_reports_channel")
    target_channel = interaction.guild.get_channel(channel_id)
    if not target_channel:
        await interaction.response.send_message("❌ Canal admin non configuré", ephemeral=True)
        return

    await target_channel.send(f"🚨 Signalement de {member.mention} par {interaction.user.mention}\n💬 Raison : {reason}")
    await interaction.response.send_message("📝 Signalement envoyé à l'administration", ephemeral=True)

# 🏆 /top_vocal — Classement des vocaux
voice_time = {}  # Peut être importé depuis manager si tu veux le centraliser

@app_commands.command(name="top_vocal", description="Classement vocal des membres (top 10)")
async def top_vocal(interaction: discord.Interaction):
    leaderboard = sorted(voice_time.items(), key=lambda x: x[1], reverse=True)[:10]
    listing = "\n".join([f"{interaction.guild.get_member(uid).mention} : {int(sec // 60)} min" for uid, sec in leaderboard])
    await interaction.response.send_message(f"🏆 Top vocal :\n{listing}", ephemeral=True)

# 💬 /top_messages — Classement messages envoyés
message_count = {}  # Peut être importé depuis tracker

@app_commands.command(name="top_messages", description="Classement des membres actifs par messages")
async def top_messages(interaction: discord.Interaction):
    top = sorted(message_count.items(), key=lambda x: x[1], reverse=True)[:10]
    output = "\n".join([f"{interaction.guild.get_member(uid).mention} : {count} messages" for uid, count in top])
    await interaction.response.send_message(f"💬 Top messages :\n{output}", ephemeral=True)


import discord
from discord import app_commands
import asyncio, random, math

# ✨ /random_quote — Citation inspirante
@app_commands.command(name="random_quote", description="Affiche une citation motivante")
async def random_quote(interaction: discord.Interaction):
    quotes = [
        "💡 La vie est un défi à relever, pas une bataille à fuir.",
        "🧠 Le succès appartient à ceux qui n’abandonnent jamais.",
        "🌟 Ta seule limite, c’est toi-même.",
    ]
    await interaction.response.send_message(random.choice(quotes), ephemeral=True)

# 🎡 /spin_wheel — Choix aléatoire parmi options
@app_commands.command(name="spin_wheel", description="Tourne une roue et choisit une option")
@app_commands.describe(options="Options séparées par des virgules")
async def spin_wheel(interaction: discord.Interaction, options: str):
    opts = [o.strip() for o in options.split(",") if o.strip()]
    if len(opts) < 2:
        await interaction.response.send_message("❌ Au moins 2 options requises", ephemeral=True)
        return
    choice = random.choice(opts)
    await interaction.response.send_message(f"🎯 Résultat : **{choice}**", ephemeral=True)

# 🌀 /mock_text — Texte sarcastique
@app_commands.command(name="mock_text", description="Transforme un texte en version sarcastique")
@app_commands.describe(text="Texte à modifier")
async def mock_text(interaction: discord.Interaction, text: str):
    mocked = "".join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text)])
    await interaction.response.send_message(f"🌀 {mocked}", ephemeral=True)

# 🎲 /random_dice — Lance un dé
@app_commands.command(name="random_dice", description="Lance un dé à X faces")
@app_commands.describe(faces="Nombre de faces du dé (≥2)")
async def random_dice(interaction: discord.Interaction, faces: int):
    if faces < 2:
        await interaction.response.send_message("❌ Minimum 2 faces", ephemeral=True)
        return
    result = random.randint(1, faces)
    await interaction.response.send_message(f"🎲 Résultat du dé à {faces} faces : **{result}**", ephemeral=True)

# 🎱 /magic_8ball — Réponse mystique
@app_commands.command(name="magic_8ball", description="Pose une question et reçois une réponse mystique")
@app_commands.describe(question="Ta question")
async def magic_8ball(interaction: discord.Interaction, question: str):
    responses = [
        "Oui, absolument ✅", "Non, jamais ❌", "Peut-être 🤷", "Demande plus tard 🕒", "C’est certain 🧠"
    ]
    await interaction.response.send_message(f"🎱 {random.choice(responses)}", ephemeral=True)

# 🧠 /calculate — Calcule une expression
@app_commands.command(name="calculate", description="Calcule une opération mathématique")
@app_commands.describe(expression="Expression (ex: 5+5*2)")
async def calculate(interaction: discord.Interaction, expression: str):
    try:
        result = eval(expression, {"__builtins__": None}, math.__dict__)
        await interaction.response.send_message(f"🧠 Résultat : `{expression}` = **{result}**", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# 🕰️ /reminder — Rappel différé
@app_commands.command(name="reminder", description="Crée un rappel dans X secondes")
@app_commands.describe(message="Message à rappeler", delay="Délai en secondes")
async def reminder(interaction: discord.Interaction, message: str, delay: int):
    await interaction.response.send_message(f"⏰ Rappel enregistré pour dans {delay} secondes", ephemeral=True)
    await asyncio.sleep(delay)
    await interaction.user.send(f"⏰ Rappel : {message}")

# 🎮 /game_picker — Propose un jeu à tester
@app_commands.command(name="game_picker", description="Propose un jeu aléatoire")
async def game_picker(interaction: discord.Interaction):
    games = ["Among Us", "Minecraft", "Valorant", "League of Legends", "Apex Legends", "Rocket League"]
    await interaction.response.send_message(f"🎮 Pourquoi pas : **{random.choice(games)}** ?", ephemeral=True)

# 💬 /reaction_role — Attribue un rôle via réaction
@app_commands.command(name="reaction_role", description="Ajoute un rôle sur réaction")
@app_commands.describe(message_id="ID du message", emoji="Emoji", role="Rôle à attribuer")
async def reaction_role(interaction: discord.Interaction, message_id: int, emoji: str, role: discord.Role):
    try:
        msg = await interaction.channel.fetch_message(message_id)
        await msg.add_reaction(emoji)
        await interaction.response.send_message(f"✅ Réaction ajoutée — les membres auront **{role.name}** en cliquant {emoji}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

import discord
from discord import app_commands
import random, datetime

# 🐱 /chuck_norris_joke — Blague Chuck Norris
@app_commands.command(name="chuck_norris_joke", description="Affiche une blague aléatoire sur Chuck Norris")
async def chuck_norris_joke(interaction: discord.Interaction):
    jokes = [
        "Chuck Norris peut diviser par zéro.",
        "Quand Chuck Norris entre dans une pièce, il éteint l'obscurité.",
        "Chuck Norris ne fait pas de pompes — il repousse la Terre."
    ]
    await interaction.response.send_message(random.choice(jokes), ephemeral=True)

# 🧪 /anime_quote — Citation inspirante d’anime
@app_commands.command(name="anime_quote", description="Affiche une citation inspirante d’un anime")
@app_commands.describe(anime="Nom de l’anime (optionnel)")
async def anime_quote(interaction: discord.Interaction, anime: str = None):
    quotes = {
        "Naruto": ["Je ne reviendrai jamais sur ma parole, c’est ma voie du ninja !"],
        "One Piece": ["Je vais être le roi des pirates !"],
        "Attack on Titan": ["Si je ne peux plus, je continuerai. Si je tombe, je me relèverai."]
    }
    q = quotes.get(anime, random.choice(list(quotes.values())))
    await interaction.response.send_message(f"🎌 {random.choice(q)}", ephemeral=True)

# 🎯 /random_member — Choisit un membre aléatoire dans un salon vocal
@app_commands.command(name="random_member", description="Choisit un membre aléatoire d’un vocal")
@app_commands.describe(channel="Salon vocal à analyser")
async def random_member(interaction: discord.Interaction, channel: discord.VoiceChannel):
    members = channel.members
    if not members:
        await interaction.response.send_message("❌ Salon vide", ephemeral=True)
        return
    chosen = random.choice(members)
    await interaction.response.send_message(f"🎯 Membre choisi : {chosen.mention}", ephemeral=True)

# 🏆 /leaderboard — Simulé
@app_commands.command(name="leaderboard", description="Classement fictif de serveurs")
async def leaderboard(interaction: discord.Interaction):
    ranking = [
        {"name": "Server Alpha", "score": 1200},
        {"name": "Server Beta", "score": 980},
        {"name": "Server Gamma", "score": 850}
    ]
    embed = discord.Embed(title="🏆 Classement des serveurs", color=discord.Color.gold())
    for rank, entry in enumerate(ranking, 1):
        embed.add_field(name=f"{rank}. {entry['name']}", value=f"Score : {entry['score']}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# 📅 /version — Affiche changelog
@app_commands.command(name="version", description="Affiche la version actuelle du bot")
async def version(interaction: discord.Interaction):
    from manager.config_manager import config_data
    v = config_data.get("bot_version", "inconnue")
    changelog = config_data.get("changelog", {}).get(v)
    embed = discord.Embed(title=f"📦 Version Arsenal : {v}", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
    if changelog:
        for line in changelog:
            embed.add_field(name="➤", value=line, inline=False)
    else:
        embed.description = "Aucun changelog disponible."
    embed.set_footer(text="Arsenal Admin Studio")
    await interaction.response.send_message(embed=embed, ephemeral=True)


import discord
from discord import app_commands
from discord.ui import Modal, TextInput
from datetime import datetime
import json, logging

class BugReportModal(Modal):
    def __init__(self):
        super().__init__(title="🐞 Signaler un bug")
        self.commande = TextInput(label="Commande concernée", placeholder="/nom_commande", required=True)
        self.details = TextInput(label="Détails du bug", style=discord.TextStyle.paragraph, placeholder="Explique ce qui ne fonctionne pas…", required=True)
        self.add_item(self.commande)
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cmd_name = self.commande.value.strip()
            bug_text = self.details.value.strip()

            if not cmd_name or not bug_text:
                await interaction.response.send_message("❌ Les champs doivent être remplis.", ephemeral=True)
                return

            # Charger les bugs existants
            try:
                with open("bug_reports.json", "r", encoding="utf-8") as f:
                    bug_data = json.load(f)
            except FileNotFoundError:
                bug_data = {}

            # Ajouter le nouveau bug
            bug_data.setdefault(cmd_name, []).append({
                "details": bug_text,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": interaction.user.id,
                "user_name": interaction.user.name
            })

            # Sauvegarder
            with open("bug_reports.json", "w", encoding="utf-8") as f:
                json.dump(bug_data, f, indent=4)

            # Embed de confirmation
            embed = discord.Embed(title="📬 Bug signalé", color=discord.Color.red())
            embed.add_field(name="Commande concernée", value=cmd_name, inline=False)
            embed.add_field(name="Détails", value=bug_text, inline=False)
            embed.set_footer(text="Merci pour ton retour !")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # DM au créateur
            creator = await interaction.client.fetch_user(431359112039890945)
            await creator.send(f"🐞 Nouveau bug signalé\nCommande : `{cmd_name}`\nPar : {interaction.user.name}\nDétails : {bug_text}")

        except Exception as e:
            logging.error(f"[BUG_REPORT] Erreur : {e}")
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

@app_commands.command(name="signaler_bug", description="Signaler un bug sur le bot Arsenal")
async def signaler_bug(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(BugReportModal())
    except Exception as e:
        logging.error(f"[BUG_MODAL] Erreur ouverture modal : {e}")
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

import subprocess
import threading

# 🖥️ /membergui — Ouvre le panel membre local
@app_commands.command(name="membergui", description="Ouvre le panel membre Arsenal")
async def membergui(interaction: discord.Interaction):
    await interaction.response.send_message("Ouverture du panel membre...", ephemeral=True)
    # Vérifie et installe les packages nécessaires
    try:
        import tkinter
    except ImportError:
        subprocess.run(["pip", "install", "tk"])
    # Lance le GUI membre en thread pour ne pas bloquer le bot
    from gui.MemberPanel import lancer_member_interface
    def run_gui():
        user_id = interaction.user.id
        server_id = interaction.guild.id
        # Fonction pour récupérer les infos Discord (à adapter si besoin)
        def get_discord_data(server_id):
            guild = interaction.guild
            return {
                "name": guild.name,
                "owner": guild.owner.name if guild.owner else "Inconnu",
                "members": [{"id": m.id, "name": m.name, "main_role": m.top_role.name, "joined_at": str(m.joined_at)} for m in guild.members],
                "roles": [{"id": r.id, "name": r.name, "count": len(r.members)} for r in guild.roles],
                "created_at": str(guild.created_at)
            }
        lancer_member_interface(user_id, server_id, get_discord_data)
    threading.Thread(target=run_gui).start()