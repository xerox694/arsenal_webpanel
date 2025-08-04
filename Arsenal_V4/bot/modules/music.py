"""
🎵 Arsenal V4 - Module Musique
==============================

Système de musique complet avec YouTube, Spotify et playlists
"""

import discord
from discord.ext import commands
import asyncio
import youtube_dl
import sqlite3
from typing import Optional, List
import re
import json
from collections import deque
import time

# Configuration YouTube-DL
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    """Source audio YouTube"""
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.uploader = data.get('uploader')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Créer une source depuis une URL"""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]
        
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
    @classmethod
    async def search_youtube(cls, query, *, loop=None):
        """Rechercher sur YouTube"""
        loop = loop or asyncio.get_event_loop()
        
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False))
            
            if 'entries' in data and data['entries']:
                return data['entries'][0]
            return None
            
        except Exception as e:
            print(f"Erreur recherche YouTube: {e}")
            return None

class MusicQueue:
    """Système de queue pour la musique"""
    
    def __init__(self):
        self.queue = deque()
        self.history = deque(maxlen=50)
        self.current = None
        self.loop = False
        self.shuffle = False
    
    def add(self, song):
        """Ajouter une chanson à la queue"""
        self.queue.append(song)
    
    def next(self):
        """Passer à la chanson suivante"""
        if self.current:
            self.history.append(self.current)
        
        if self.loop and self.current:
            self.queue.appendleft(self.current)
        
        self.current = self.queue.popleft() if self.queue else None
        return self.current
    
    def clear(self):
        """Vider la queue"""
        self.queue.clear()
        self.current = None
    
    def remove(self, index):
        """Retirer une chanson par index"""
        if 0 <= index < len(self.queue):
            return self.queue.remove(self.queue[index])
        return None
    
    def get_queue_list(self, limit=10):
        """Obtenir la liste de la queue"""
        return list(self.queue)[:limit]

class MusicPlayer:
    """Lecteur de musique pour un serveur"""
    
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.queue = MusicQueue()
        self.voice_client = None
        self.volume = 0.5
        self.is_playing = False
        self.skip_votes = set()
        self.skip_threshold = 3
    
    async def connect(self, channel):
        """Se connecter à un canal vocal"""
        if self.voice_client:
            await self.voice_client.move_to(channel)
        else:
            self.voice_client = await channel.connect()
    
    async def disconnect(self):
        """Se déconnecter du canal vocal"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        self.queue.clear()
        self.is_playing = False
    
    async def play_next(self):
        """Jouer la chanson suivante"""
        if not self.voice_client:
            return
        
        song = self.queue.next()
        
        if song:
            try:
                source = await YTDLSource.from_url(song['url'], stream=True)
                source.volume = self.volume
                
                self.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
                self.is_playing = True
                self.skip_votes.clear()
                
                # Notifier le canal
                if hasattr(self, 'text_channel'):
                    embed = discord.Embed(
                        title="🎵 En cours de lecture",
                        description=f"[{song['title']}]({song['url']})",
                        color=0x1db954
                    )
                    embed.add_field(name="Durée", value=self.format_duration(song.get('duration', 0)), inline=True)
                    embed.add_field(name="Demandé par", value=song.get('requester', 'Inconnu'), inline=True)
                    
                    if song.get('thumbnail'):
                        embed.set_thumbnail(url=song['thumbnail'])
                    
                    await self.text_channel.send(embed=embed)
                
            except Exception as e:
                print(f"Erreur lecture: {e}")
                await self.play_next()
        else:
            self.is_playing = False
    
    def format_duration(self, seconds):
        """Formater la durée"""
        if not seconds:
            return "Inconnu"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    def vote_skip(self, user_id):
        """Vote pour skip"""
        self.skip_votes.add(user_id)
        return len(self.skip_votes)

class MusicModule(commands.Cog):
    """Module de musique pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
    
    def get_player(self, guild):
        """Obtenir le lecteur d'un serveur"""
        if guild.id not in self.players:
            self.players[guild.id] = MusicPlayer(self.bot, guild)
        return self.players[guild.id]
    
    @commands.command(name='join', aliases=['connect'])
    async def join_voice(self, ctx):
        """🔗 Rejoindre votre canal vocal"""
        
        if not ctx.author.voice:
            return await ctx.send("❌ Vous devez être dans un canal vocal !")
        
        channel = ctx.author.voice.channel
        player = self.get_player(ctx.guild)
        
        await player.connect(channel)
        player.text_channel = ctx.channel
        
        embed = discord.Embed(
            title="✅ Connecté",
            description=f"Connecté à **{channel.name}**",
            color=0x00ff41
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='leave', aliases=['disconnect'])
    async def leave_voice(self, ctx):
        """❌ Quitter le canal vocal"""
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client:
            return await ctx.send("❌ Je ne suis pas connecté à un canal vocal !")
        
        await player.disconnect()
        
        embed = discord.Embed(
            title="✅ Déconnecté",
            description="Déconnecté du canal vocal",
            color=0xff4757
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='play', aliases=['p'])
    async def play_music(self, ctx, *, query):
        """🎵 Jouer de la musique"""
        
        player = self.get_player(ctx.guild)
        
        # Se connecter si pas déjà connecté
        if not player.voice_client:
            if not ctx.author.voice:
                return await ctx.send("❌ Vous devez être dans un canal vocal !")
            await player.connect(ctx.author.voice.channel)
            player.text_channel = ctx.channel
        
        # Message de recherche
        search_msg = await ctx.send("🔍 Recherche en cours...")
        
        # Rechercher la musique
        if query.startswith(('http://', 'https://')):
            # URL directe
            try:
                data = await YTDLSource.search_youtube(query)
                if not data:
                    return await search_msg.edit(content="❌ Impossible de charger cette URL !")
            except Exception as e:
                return await search_msg.edit(content=f"❌ Erreur: {e}")
        else:
            # Recherche YouTube
            data = await YTDLSource.search_youtube(query)
            if not data:
                return await search_msg.edit(content="❌ Aucun résultat trouvé !")
        
        # Ajouter à la queue
        song = {
            'title': data['title'],
            'url': data['webpage_url'],
            'duration': data.get('duration'),
            'thumbnail': data.get('thumbnail'),
            'uploader': data.get('uploader'),
            'requester': ctx.author.mention
        }
        
        player.queue.add(song)
        
        # Jouer si rien n'est en cours
        if not player.is_playing:
            await player.play_next()
            await search_msg.delete()
        else:
            # Ajouter à la queue
            embed = discord.Embed(
                title="➕ Ajouté à la queue",
                description=f"[{song['title']}]({song['url']})",
                color=0x3498db
            )
            
            embed.add_field(name="Position", value=f"#{len(player.queue.queue)}", inline=True)
            embed.add_field(name="Durée", value=player.format_duration(song.get('duration', 0)), inline=True)
            embed.add_field(name="Demandé par", value=ctx.author.mention, inline=True)
            
            if song.get('thumbnail'):
                embed.set_thumbnail(url=song['thumbnail'])
            
            await search_msg.edit(content="", embed=embed)
    
    @commands.command(name='skip', aliases=['s'])
    async def skip_song(self, ctx):
        """⏭️ Passer la chanson actuelle"""
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client or not player.is_playing:
            return await ctx.send("❌ Aucune musique en cours !")
        
        # Vérifier les permissions
        if ctx.author.guild_permissions.manage_messages:
            # Skip direct pour les modérateurs
            player.voice_client.stop()
            await ctx.send("⏭️ Chanson passée par un modérateur !")
            return
        
        # Vote pour skip
        votes = player.vote_skip(ctx.author.id)
        
        # Calculer le seuil (1/3 des membres connectés)
        voice_members = len([m for m in player.voice_client.channel.members if not m.bot])
        threshold = max(1, voice_members // 3)
        
        if votes >= threshold:
            player.voice_client.stop()
            embed = discord.Embed(
                title="⏭️ Chanson passée",
                description=f"Vote réussi ({votes}/{threshold})",
                color=0x00ff41
            )
        else:
            embed = discord.Embed(
                title="🗳️ Vote pour skip",
                description=f"Votes: {votes}/{threshold}",
                color=0xffaa00
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='queue', aliases=['q'])
    async def show_queue(self, ctx):
        """📝 Afficher la queue"""
        
        player = self.get_player(ctx.guild)
        
        if not player.queue.queue:
            return await ctx.send("❌ La queue est vide !")
        
        embed = discord.Embed(
            title="📝 Queue de musique",
            color=0x3498db
        )
        
        # Chanson actuelle
        if player.queue.current:
            current = player.queue.current
            embed.add_field(
                name="🎵 En cours",
                value=f"[{current['title']}]({current['url']})",
                inline=False
            )
        
        # Queue
        queue_list = player.queue.get_queue_list(10)
        if queue_list:
            queue_text = []
            for i, song in enumerate(queue_list, 1):
                duration = player.format_duration(song.get('duration', 0))
                queue_text.append(f"`{i}.` [{song['title']}]({song['url']}) - `{duration}`")
            
            embed.add_field(
                name="📋 Prochaines chansons",
                value="\n".join(queue_text),
                inline=False
            )
        
        # Info queue
        total_songs = len(player.queue.queue)
        embed.set_footer(text=f"Total: {total_songs} chanson{'s' if total_songs > 1 else ''}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing(self, ctx):
        """🎵 Chanson actuelle"""
        
        player = self.get_player(ctx.guild)
        
        if not player.is_playing or not player.queue.current:
            return await ctx.send("❌ Aucune musique en cours !")
        
        song = player.queue.current
        
        embed = discord.Embed(
            title="🎵 En cours de lecture",
            description=f"[{song['title']}]({song['url']})",
            color=0x1db954
        )
        
        embed.add_field(name="Durée", value=player.format_duration(song.get('duration', 0)), inline=True)
        embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%", inline=True)
        embed.add_field(name="Demandé par", value=song.get('requester', 'Inconnu'), inline=True)
        
        if song.get('uploader'):
            embed.add_field(name="Chaîne", value=song['uploader'], inline=True)
        
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume', aliases=['v'])
    async def set_volume(self, ctx, volume: int):
        """🔊 Changer le volume (0-100)"""
        
        if not 0 <= volume <= 100:
            return await ctx.send("❌ Le volume doit être entre 0 et 100 !")
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client:
            return await ctx.send("❌ Je ne suis pas connecté !")
        
        player.volume = volume / 100
        
        if player.voice_client.source:
            player.voice_client.source.volume = player.volume
        
        embed = discord.Embed(
            title="🔊 Volume modifié",
            description=f"Volume réglé à **{volume}%**",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='pause')
    async def pause_music(self, ctx):
        """⏸️ Mettre en pause"""
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client or not player.voice_client.is_playing():
            return await ctx.send("❌ Aucune musique en cours !")
        
        player.voice_client.pause()
        
        embed = discord.Embed(
            title="⏸️ Musique en pause",
            color=0xffaa00
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='resume')
    async def resume_music(self, ctx):
        """▶️ Reprendre la lecture"""
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client or not player.voice_client.is_paused():
            return await ctx.send("❌ Aucune musique en pause !")
        
        player.voice_client.resume()
        
        embed = discord.Embed(
            title="▶️ Lecture reprise",
            color=0x00ff41
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='stop')
    async def stop_music(self, ctx):
        """⏹️ Arrêter la musique"""
        
        player = self.get_player(ctx.guild)
        
        if not player.voice_client:
            return await ctx.send("❌ Je ne suis pas connecté !")
        
        player.voice_client.stop()
        player.queue.clear()
        
        embed = discord.Embed(
            title="⏹️ Musique arrêtée",
            description="Queue vidée",
            color=0xff4757
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear')
    async def clear_queue(self, ctx):
        """🧹 Vider la queue"""
        
        player = self.get_player(ctx.guild)
        
        if not player.queue.queue:
            return await ctx.send("❌ La queue est déjà vide !")
        
        songs_count = len(player.queue.queue)
        player.queue.clear()
        
        embed = discord.Embed(
            title="🧹 Queue vidée",
            description=f"{songs_count} chanson{'s' if songs_count > 1 else ''} supprimée{'s' if songs_count > 1 else ''}",
            color=0x00ff41
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='remove')
    async def remove_song(self, ctx, index: int):
        """🗑️ Retirer une chanson de la queue"""
        
        player = self.get_player(ctx.guild)
        
        if not player.queue.queue:
            return await ctx.send("❌ La queue est vide !")
        
        if not 1 <= index <= len(player.queue.queue):
            return await ctx.send(f"❌ Index invalide ! (1-{len(player.queue.queue)})")
        
        removed_song = player.queue.remove(index - 1)
        
        if removed_song:
            embed = discord.Embed(
                title="🗑️ Chanson supprimée",
                description=f"[{removed_song['title']}]({removed_song['url']})",
                color=0xff4757
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Erreur lors de la suppression !")
    
    @commands.command(name='loop', aliases=['repeat'])
    async def toggle_loop(self, ctx):
        """🔄 Activer/désactiver la répétition"""
        
        player = self.get_player(ctx.guild)
        player.queue.loop = not player.queue.loop
        
        status = "activée" if player.queue.loop else "désactivée"
        emoji = "🔄" if player.queue.loop else "⏹️"
        
        embed = discord.Embed(
            title=f"{emoji} Répétition {status}",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='shuffle')
    async def shuffle_queue(self, ctx):
        """🔀 Mélanger la queue"""
        
        player = self.get_player(ctx.guild)
        
        if len(player.queue.queue) < 2:
            return await ctx.send("❌ Pas assez de chansons dans la queue !")
        
        import random
        queue_list = list(player.queue.queue)
        random.shuffle(queue_list)
        player.queue.queue = deque(queue_list)
        
        embed = discord.Embed(
            title="🔀 Queue mélangée",
            description=f"{len(queue_list)} chansons mélangées",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MusicModule(bot))
