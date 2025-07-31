import discord
from discord import app_commands
from discord.ext import commands
from core.config_loader import FFMPEG_OPTIONS
from yt_dlp import YoutubeDL

# 🎧 Groupe Slash pour regrouper tes commandes musique
music_group = app_commands.Group(name="music", description="Commandes audio Arsenal")

# 🧠 /music play
@music_group.command(name="play", description="Joue une musique via URL YouTube")
@app_commands.describe(url="Lien YouTube")
async def play(interaction: discord.Interaction, url: str):
    voice = interaction.user.voice
    if not voice or not voice.channel:
        await interaction.response.send_message("❌ Tu dois être dans un salon vocal.", ephemeral=True)
        return

    channel = voice.channel
    vc = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
    if not vc:
        vc = await channel.connect()

    try:
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'quiet': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
            await interaction.response.send_message(f"🎶 Lecture en cours : {info['title']}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

# ⏸️ /music pause
@music_group.command(name="pause", description="Met la musique en pause")
async def pause(interaction: discord.Interaction):
    vc = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Musique mise en pause")
    else:
        await interaction.response.send_message("❌ Rien à mettre en pause", ephemeral=True)

# ▶️ /music resume
@music_group.command(name="resume", description="Reprend la musique en pause")
async def resume(interaction: discord.Interaction):
    vc = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Musique reprise")
    else:
        await interaction.response.send_message("❌ Aucune musique en pause", ephemeral=True)

# 🔇 /music stop
@music_group.command(name="stop", description="Arrête la musique et quitte le vocal")
async def stop(interaction: discord.Interaction):
    vc = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
    if vc:
        vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("🛑 Musique arrêtée et déconnecté.")
    else:
        await interaction.response.send_message("❌ Le bot n’est pas connecté au vocal", ephemeral=True)

# 🔧 Setup pour main.py
def setup_audio(client: commands.Bot):
    try:
        client.tree.add_command(music_group)
    except Exception as e:
        print(f"[MUSIC SETUP] Erreur : {e}")