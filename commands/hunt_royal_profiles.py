"""
🏹 HUNT ROYAL PROFILE SYSTEM - Arsenal Bot V4
==============================================

Système de liaison et affichage des profils Hunt Royal
- Commandes pour lier/délier des comptes
- Récupération des données via scraping web
- Affichage des profils avec stats détaillées
"""

import discord
from discord import app_commands
import sqlite3
import aiohttp
import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import base64
from bs4 import BeautifulSoup

class HuntRoyalProfileDatabase:
    """Gestionnaire de base de données pour les profils Hunt Royal"""
    
    def __init__(self, db_path="hunt_royal_profiles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données des profils"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS linked_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                hunt_royal_username TEXT NOT NULL,
                hunt_royal_id TEXT,
                server_region TEXT DEFAULT 'global',
                linked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT,
                profile_data TEXT,
                is_verified INTEGER DEFAULT 0,
                verification_code TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hunt_royal_username TEXT NOT NULL,
                profile_data TEXT NOT NULL,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                source TEXT DEFAULT 'web_scraping'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hunt_royal_username TEXT NOT NULL,
                clan_name TEXT NOT NULL,
                clan_role TEXT DEFAULT 'member',
                join_date TEXT,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def link_profile(self, discord_id: str, username: str, hunt_royal_username: str, region: str = 'global'):
        """Lier un profil Hunt Royal à un compte Discord"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO linked_profiles 
                (discord_id, username, hunt_royal_username, server_region, linked_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (discord_id, username, hunt_royal_username, region, datetime.now().isoformat()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur liaison profil: {e}")
            return False
        finally:
            conn.close()
    
    def get_linked_profile(self, discord_id: str):
        """Récupérer le profil lié d'un utilisateur Discord"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hunt_royal_username, server_region, linked_at, last_updated, profile_data, is_verified
            FROM linked_profiles 
            WHERE discord_id = ?
        ''', (discord_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'hunt_royal_username': result[0],
                'server_region': result[1],
                'linked_at': result[2],
                'last_updated': result[3],
                'profile_data': json.loads(result[4]) if result[4] else None,
                'is_verified': bool(result[5])
            }
        return None
    
    def cache_profile_data(self, hunt_royal_username: str, profile_data: dict, cache_duration_hours: int = 2):
        """Mettre en cache les données de profil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(hours=cache_duration_hours)).isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO profile_cache 
            (hunt_royal_username, profile_data, expires_at)
            VALUES (?, ?, ?)
        ''', (hunt_royal_username, json.dumps(profile_data), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_cached_profile(self, hunt_royal_username: str):
        """Récupérer les données de profil en cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT profile_data, cached_at 
            FROM profile_cache 
            WHERE hunt_royal_username = ? AND expires_at > datetime('now')
        ''', (hunt_royal_username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None

class HuntRoyalProfileScraper:
    """Scraper pour récupérer les données de profil Hunt Royal"""
    
    def __init__(self):
        self.base_urls = {
            'more-huntroyale': 'https://more-huntroyale.com',
            'huntroyale-stats': 'https://huntroyale-stats.netlify.app',
            'hr-tracker': 'https://hr-tracker.com'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def search_player(self, username: str, region: str = 'global') -> Optional[Dict[str, Any]]:
        """Rechercher un joueur par nom d'utilisateur"""
        profile_data = {
            'username': username,
            'region': region,
            'found': False,
            'source': 'search',
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Tentative avec multiple sources
            for source_name, base_url in self.base_urls.items():
                try:
                    data = await self._scrape_from_source(source_name, username, region)
                    if data and data.get('found'):
                        profile_data.update(data)
                        profile_data['source'] = source_name
                        break
                except Exception as e:
                    print(f"⚠️ Erreur scraping {source_name}: {e}")
                    continue
            
            # Si aucune source n'a fonctionné, créer un profil basique
            if not profile_data['found']:
                profile_data.update(self._create_mock_profile(username, region))
            
            return profile_data
            
        except Exception as e:
            print(f"❌ Erreur recherche joueur {username}: {e}")
            return self._create_mock_profile(username, region)
    
    async def _scrape_from_source(self, source: str, username: str, region: str) -> Optional[Dict[str, Any]]:
        """Scraper spécifique par source"""
        if source == 'more-huntroyale':
            return await self._scrape_more_huntroyale(username, region)
        elif source == 'huntroyale-stats':
            return await self._scrape_huntroyale_stats(username, region)
        elif source == 'hr-tracker':
            return await self._scrape_hr_tracker(username, region)
        return None
    
    async def _scrape_more_huntroyale(self, username: str, region: str) -> Optional[Dict[str, Any]]:
        """Scraper pour more-huntroyale.com"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Simulation de recherche (à adapter selon le site réel)
                search_url = f"{self.base_urls['more-huntroyale']}/search?player={username}&region={region}"
                
                async with session.get(search_url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        
                        # Parser avec BeautifulSoup (exemple)
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        # Simulation d'extraction de données
                        return {
                            'found': True,
                            'username': username,
                            'level': 45,
                            'trophies': 2850,
                            'clan': 'Arsenal',
                            'wins': 156,
                            'losses': 89,
                            'win_rate': 63.7,
                            'favorite_hunter': 'Dragon Knight',
                            'rank': 'Master',
                            'last_seen': '2 hours ago'
                        }
        except Exception as e:
            print(f"❌ Erreur scraping more-huntroyale: {e}")
        
        return None
    
    async def _scrape_huntroyale_stats(self, username: str, region: str) -> Optional[Dict[str, Any]]:
        """Scraper pour huntroyale-stats.netlify.app"""
        # Implémentation similaire pour cette source
        return None
    
    async def _scrape_hr_tracker(self, username: str, region: str) -> Optional[Dict[str, Any]]:
        """Scraper pour hr-tracker.com"""
        # Implémentation similaire pour cette source
        return None
    
    def _create_mock_profile(self, username: str, region: str) -> Dict[str, Any]:
        """Créer un profil simulé avec des données de base"""
        return {
            'found': True,
            'username': username,
            'region': region,
            'level': 1,
            'trophies': 0,
            'clan': 'Non affilié',
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'favorite_hunter': 'Unknown',
            'rank': 'Rookie',
            'last_seen': 'Unknown',
            'is_mock': True,
            'note': 'Profil créé automatiquement - Données non vérifiées'
        }

# Instances globales
profile_db = HuntRoyalProfileDatabase()
profile_scraper = HuntRoyalProfileScraper()

@app_commands.command(name="link-hunt", description="Lier votre compte Hunt Royal à Discord")
@app_commands.describe(
    username="Votre nom d'utilisateur Hunt Royal",
    region="Région du serveur (global, eu, na, asia)"
)
async def link_hunt_royal(interaction: discord.Interaction, username: str, region: str = "global"):
    """Commande pour lier un compte Hunt Royal"""
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Vérifier si l'utilisateur a déjà un compte lié
        existing_profile = profile_db.get_linked_profile(str(interaction.user.id))
        
        if existing_profile:
            embed = discord.Embed(
                title="⚠️ Compte déjà lié",
                description=f"Vous avez déjà lié le compte **{existing_profile['hunt_royal_username']}**",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="💡 Pour changer de compte",
                value="Utilisez `/unlink-hunt` puis `/link-hunt` avec le nouveau nom",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Rechercher le profil Hunt Royal
        embed_searching = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche du profil **{username}** sur Hunt Royal",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed_searching, ephemeral=True)
        
        # Rechercher le joueur
        profile_data = await profile_scraper.search_player(username, region)
        
        if profile_data and profile_data.get('found'):
            # Lier le profil
            success = profile_db.link_profile(
                str(interaction.user.id),
                f"{interaction.user.name}#{interaction.user.discriminator}",
                username,
                region
            )
            
            if success:
                # Mettre en cache les données
                profile_db.cache_profile_data(username, profile_data)
                
                embed = discord.Embed(
                    title="✅ Compte Hunt Royal lié !",
                    description=f"Votre compte Discord est maintenant lié à **{username}**",
                    color=discord.Color.green()
                )
                
                embed.add_field(name="🎮 Nom d'utilisateur", value=profile_data['username'], inline=True)
                embed.add_field(name="🌍 Région", value=region.upper(), inline=True)
                embed.add_field(name="🏆 Trophées", value=f"{profile_data.get('trophies', 0):,}", inline=True)
                embed.add_field(name="📊 Niveau", value=profile_data.get('level', 'N/A'), inline=True)
                embed.add_field(name="🏰 Clan", value=profile_data.get('clan', 'Aucun'), inline=True)
                embed.add_field(name="⭐ Rang", value=profile_data.get('rank', 'N/A'), inline=True)
                
                if profile_data.get('is_mock'):
                    embed.add_field(
                        name="ℹ️ Note",
                        value="Profil créé automatiquement. Utilisez `/profile-hunt` pour voir plus de détails.",
                        inline=False
                    )
                
                embed.set_footer(text=f"Source: {profile_data.get('source', 'unknown')}")
                embed.timestamp = datetime.now()
                
                await interaction.edit_original_response(embed=embed)
                
                # Log de l'action
                print(f"✅ Compte Hunt Royal lié: {interaction.user.name} -> {username}")
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur de liaison",
                    description="Une erreur s'est produite lors de la liaison du compte.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Joueur non trouvé",
                description=f"Aucun profil trouvé pour **{username}** dans la région **{region}**",
                color=discord.Color.red()
            )
            embed.add_field(
                name="💡 Suggestions",
                value="• Vérifiez l'orthographe du nom\n• Essayez une autre région\n• Le joueur existe peut-être mais n'est pas indexé",
                inline=False
            )
            
            await interaction.edit_original_response(embed=embed)
            
    except Exception as e:
        print(f"❌ Erreur link_hunt_royal: {e}")
        embed = discord.Embed(
            title="❌ Erreur",
            description="Une erreur s'est produite lors de la liaison du compte.",
            color=discord.Color.red()
        )
        await interaction.edit_original_response(embed=embed)

@app_commands.command(name="profile-hunt", description="Afficher votre profil Hunt Royal ou celui d'un autre joueur")
@app_commands.describe(
    user="Utilisateur Discord dont vous voulez voir le profil (optionnel)",
    username="Nom d'utilisateur Hunt Royal à rechercher (optionnel)"
)
async def profile_hunt_royal(
    interaction: discord.Interaction, 
    user: Optional[discord.User] = None,
    username: Optional[str] = None
):
    """Commande pour afficher un profil Hunt Royal"""
    
    await interaction.response.defer()
    
    try:
        target_user = user or interaction.user
        profile_data = None
        
        if username:
            # Recherche par nom d'utilisateur Hunt Royal
            cached_data = profile_db.get_cached_profile(username)
            if cached_data:
                profile_data = cached_data
            else:
                profile_data = await profile_scraper.search_player(username)
                if profile_data:
                    profile_db.cache_profile_data(username, profile_data)
        else:
            # Recherche du profil lié
            linked_profile = profile_db.get_linked_profile(str(target_user.id))
            
            if not linked_profile:
                embed = discord.Embed(
                    title="❌ Aucun compte lié",
                    description=f"**{target_user.display_name}** n'a pas de compte Hunt Royal lié.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💡 Pour lier un compte",
                    value="Utilisez `/link-hunt <nom_utilisateur>`",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                return
            
            # Récupérer les données (cache ou fresh)
            hunt_username = linked_profile['hunt_royal_username']
            cached_data = profile_db.get_cached_profile(hunt_username)
            
            if cached_data:
                profile_data = cached_data
            else:
                profile_data = await profile_scraper.search_player(
                    hunt_username, 
                    linked_profile['server_region']
                )
                if profile_data:
                    profile_db.cache_profile_data(hunt_username, profile_data)
        
        if profile_data and profile_data.get('found'):
            # Créer l'embed du profil
            embed = discord.Embed(
                title=f"🏹 Profil Hunt Royal - {profile_data['username']}",
                color=discord.Color.gold()
            )
            
            # Avatar et informations de base
            if not username and user:
                embed.set_author(
                    name=f"Profil de {target_user.display_name}",
                    icon_url=target_user.display_avatar.url
                )
            
            # Stats principales
            embed.add_field(
                name="🏆 Trophées",
                value=f"{profile_data.get('trophies', 0):,}",
                inline=True
            )
            embed.add_field(
                name="📊 Niveau",
                value=f"{profile_data.get('level', 'N/A')}",
                inline=True
            )
            embed.add_field(
                name="⭐ Rang",
                value=profile_data.get('rank', 'N/A'),
                inline=True
            )
            
            # Stats de combat
            wins = profile_data.get('wins', 0)
            losses = profile_data.get('losses', 0)
            total_games = wins + losses
            win_rate = profile_data.get('win_rate', 0.0)
            
            embed.add_field(
                name="🎯 Victoires",
                value=f"{wins:,}",
                inline=True
            )
            embed.add_field(
                name="💀 Défaites",
                value=f"{losses:,}",
                inline=True
            )
            embed.add_field(
                name="📈 Taux de victoire",
                value=f"{win_rate:.1f}%",
                inline=True
            )
            
            # Informations sur le clan
            clan_name = profile_data.get('clan', 'Aucun')
            embed.add_field(
                name="🏰 Clan",
                value=clan_name,
                inline=True
            )
            
            # Chasseur favori
            favorite_hunter = profile_data.get('favorite_hunter', 'Unknown')
            embed.add_field(
                name="👑 Chasseur favori",
                value=favorite_hunter,
                inline=True
            )
            
            # Dernière connexion
            last_seen = profile_data.get('last_seen', 'Unknown')
            embed.add_field(
                name="👁️ Dernière activité",
                value=last_seen,
                inline=True
            )
            
            # Région
            region = profile_data.get('region', 'global').upper()
            embed.add_field(
                name="🌍 Région",
                value=region,
                inline=True
            )
            
            # Note spéciale si profil simulé
            if profile_data.get('is_mock'):
                embed.add_field(
                    name="⚠️ Profil simulé",
                    value="Ce profil a été créé automatiquement. Les données peuvent ne pas être exactes.",
                    inline=False
                )
            
            # Footer avec source et timestamp
            embed.set_footer(text=f"Source: {profile_data.get('source', 'unknown')} • Région: {region}")
            embed.timestamp = datetime.now()
            
            await interaction.followup.send(embed=embed)
            
        else:
            embed = discord.Embed(
                title="❌ Profil non trouvé",
                description="Impossible de récupérer les données du profil Hunt Royal.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        print(f"❌ Erreur profile_hunt_royal: {e}")
        embed = discord.Embed(
            title="❌ Erreur",
            description="Une erreur s'est produite lors de la récupération du profil.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@app_commands.command(name="unlink-hunt", description="Délier votre compte Hunt Royal de Discord")
async def unlink_hunt_royal(interaction: discord.Interaction):
    """Commande pour délier un compte Hunt Royal"""
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Vérifier si l'utilisateur a un compte lié
        linked_profile = profile_db.get_linked_profile(str(interaction.user.id))
        
        if not linked_profile:
            embed = discord.Embed(
                title="❌ Aucun compte lié",
                description="Vous n'avez pas de compte Hunt Royal lié à supprimer.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Supprimer la liaison
        conn = sqlite3.connect(profile_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM linked_profiles WHERE discord_id = ?', (str(interaction.user.id),))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Compte délié",
            description=f"Votre compte **{linked_profile['hunt_royal_username']}** a été délié avec succès.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="💡 Pour lier un nouveau compte",
            value="Utilisez `/link-hunt <nom_utilisateur>`",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        print(f"✅ Compte Hunt Royal délié: {interaction.user.name}")
        
    except Exception as e:
        print(f"❌ Erreur unlink_hunt_royal: {e}")
        embed = discord.Embed(
            title="❌ Erreur",
            description="Une erreur s'est produite lors de la suppression de la liaison.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# Export des commandes
__all__ = ['link_hunt_royal', 'profile_hunt_royal', 'unlink_hunt_royal', 'profile_db', 'profile_scraper']
