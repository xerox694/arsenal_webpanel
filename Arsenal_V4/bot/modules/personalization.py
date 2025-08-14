"""
🎨 Arsenal V4 - Module Personnalisation
=======================================

Système de personnalisation complet avec profils, avatars, et badges
"""

import discord
from discord.ext import commands
import sqlite3
import json
import asyncio
from typing import Optional, List, Dict
from datetime import datetime
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import aiohttp

class PersonalizationModule(commands.Cog):
    """Module de personnalisation pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Configuration des badges
        self.badges = {
            'developer': {'emoji': '👨‍💻', 'name': 'Développeur', 'description': 'Créateur du bot'},
            'admin': {'emoji': '👑', 'name': 'Administrateur', 'description': 'Administrateur du serveur'},
            'moderator': {'emoji': '🛡️', 'name': 'Modérateur', 'description': 'Modérateur du serveur'},
            'vip': {'emoji': '⭐', 'name': 'VIP', 'description': 'Membre VIP'},
            'active': {'emoji': '🔥', 'name': 'Actif', 'description': 'Membre très actif'},
            'helper': {'emoji': '🤝', 'name': 'Helper', 'description': 'Aide la communauté'},
            'rich': {'emoji': '💎', 'name': 'Riche', 'description': 'Plus de 100,000 ArsenalCoins'},
            'veteran': {'emoji': '🏆', 'name': 'Vétéran', 'description': 'Membre depuis plus de 6 mois'},
            'lucky': {'emoji': '🍀', 'name': 'Chanceux', 'description': 'A gagné au casino'},
            'collector': {'emoji': '📦', 'name': 'Collectionneur', 'description': 'Possède 10+ objets'},
            'social': {'emoji': '💬', 'name': 'Social', 'description': 'Plus de 1000 messages'},
            'gamer': {'emoji': '🎮', 'name': 'Gamer', 'description': 'A joué à tous les jeux'},
            'supporter': {'emoji': '❤️', 'name': 'Supporter', 'description': 'Soutient le serveur'},
            'early': {'emoji': '🚀', 'name': 'Early Bird', 'description': 'Parmi les premiers membres'}
        }
        
        # Couleurs disponibles
        self.colors = {
            'red': 0xff4757,
            'blue': 0x3498db,
            'green': 0x00ff41,
            'purple': 0xa55eea,
            'orange': 0xff7f00,
            'pink': 0xfd79a8,
            'yellow': 0xffb142,
            'cyan': 0x00ffff,
            'lime': 0x32ff7e,
            'magenta': 0xff006e,
            'gold': 0xffd700,
            'silver': 0xc0c0c0
        }
        
        # Thèmes de profil
        self.themes = {
            'default': {'bg': '#2c3e50', 'accent': '#3498db'},
            'dark': {'bg': '#1a1a1a', 'accent': '#ff4757'},
            'neon': {'bg': '#0f0f0f', 'accent': '#00ff41'},
            'ocean': {'bg': '#2980b9', 'accent': '#74b9ff'},
            'sunset': {'bg': '#fd7e14', 'accent': '#fab1a0'},
            'forest': {'bg': '#00b894', 'accent': '#81ecec'},
            'royal': {'bg': '#6c5ce7', 'accent': '#a29bfe'},
            'fire': {'bg': '#e17055', 'accent': '#fdcb6e'}
        }
    
    @commands.group(name='profile', aliases=['profil'], invoke_without_command=True)
    async def profile(self, ctx, member: discord.Member = None):
        """👤 Voir le profil d'un utilisateur"""
        
        target = member or ctx.author
        profile_data = self.get_user_profile(target.id, ctx.guild.id)
        
        # Créer la carte de profil
        profile_card = await self.create_profile_card(target, profile_data, ctx.guild)
        
        # Convertir en fichier Discord
        file = discord.File(profile_card, filename='profile.png')
        
        embed = discord.Embed(
            title=f"👤 Profil de {target.display_name}",
            color=profile_data.get('color', 0x3498db)
        )
        
        embed.set_image(url="attachment://profile.png")
        
        # Informations supplémentaires
        if profile_data.get('bio'):
            embed.add_field(name="📝 Bio", value=profile_data['bio'], inline=False)
        
        # Badges
        user_badges = self.get_user_badges(target.id, ctx.guild.id)
        if user_badges:
            badge_text = " ".join([self.badges[badge]['emoji'] for badge in user_badges if badge in self.badges])
            embed.add_field(name="🏆 Badges", value=badge_text, inline=False)
        
        await ctx.send(embed=embed, file=file)
    
    @profile.command(name='bio')
    async def set_bio(self, ctx, *, bio: str):
        """📝 Définir votre biographie"""
        
        if len(bio) > 200:
            return await ctx.send("❌ La biographie ne peut pas dépasser 200 caractères !")
        
        self.update_user_profile(ctx.author.id, ctx.guild.id, {'bio': bio})
        
        embed = discord.Embed(
            title="✅ Biographie mise à jour",
            description=f"**Nouvelle bio:** {bio}",
            color=0x00ff41
        )
        
        await ctx.send(embed=embed)
    
    @profile.command(name='color', aliases=['couleur'])
    async def set_color(self, ctx, color: str):
        """🎨 Changer la couleur de votre profil"""
        
        if color.lower() not in self.colors:
            available_colors = ", ".join(self.colors.keys())
            return await ctx.send(f"❌ Couleur invalide ! Disponibles: {available_colors}")
        
        color_value = self.colors[color.lower()]
        self.update_user_profile(ctx.author.id, ctx.guild.id, {'color': color_value})
        
        embed = discord.Embed(
            title="✅ Couleur changée",
            description=f"Votre couleur de profil est maintenant **{color}**",
            color=color_value
        )
        
        await ctx.send(embed=embed)
    
    @profile.command(name='theme', aliases=['thème'])
    async def set_theme(self, ctx, theme: str):
        """🎭 Changer le thème de votre profil"""
        
        if theme.lower() not in self.themes:
            available_themes = ", ".join(self.themes.keys())
            return await ctx.send(f"❌ Thème invalide ! Disponibles: {available_themes}")
        
        self.update_user_profile(ctx.author.id, ctx.guild.id, {'theme': theme.lower()})
        
        embed = discord.Embed(
            title="✅ Thème changé",
            description=f"Votre thème de profil est maintenant **{theme}**",
            color=0x3498db
        )
        
        await ctx.send(embed=embed)
    
    @profile.command(name='background', aliases=['bg'])
    async def set_background(self, ctx, *, url: str = None):
        """🖼️ Définir une image de fond personnalisée"""
        
        # Vérifier si l'utilisateur a une image en pièce jointe
        if not url and ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.content_type and attachment.content_type.startswith('image/'):
                url = attachment.url
            else:
                return await ctx.send("❌ Le fichier doit être une image !")
        
        if not url:
            return await ctx.send("❌ Vous devez fournir une URL d'image ou joindre un fichier !")
        
        # Vérifier si l'image est valide
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await ctx.send("❌ Impossible de télécharger l'image !")
                    
                    if resp.headers.get('content-type', '').startswith('image/'):
                        self.update_user_profile(ctx.author.id, ctx.guild.id, {'background': url})
                        
                        embed = discord.Embed(
                            title="✅ Fond d'écran mis à jour",
                            description="Votre image de fond personnalisée a été définie !",
                            color=0x00ff41
                        )
                        embed.set_image(url=url)
                        
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ L'URL ne pointe pas vers une image valide !")
        
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du téléchargement: {e}")
    
    @commands.command(name='badges')
    async def show_badges(self, ctx, member: discord.Member = None):
        """🏆 Voir les badges d'un utilisateur"""
        
        target = member or ctx.author
        user_badges = self.get_user_badges(target.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f"🏆 Badges de {target.display_name}",
            color=0xffd700
        )
        
        if not user_badges:
            embed.description = "Aucun badge pour le moment !"
        else:
            badge_list = []
            for badge in user_badges:
                if badge in self.badges:
                    badge_info = self.badges[badge]
                    badge_list.append(f"{badge_info['emoji']} **{badge_info['name']}** - {badge_info['description']}")
            
            embed.description = "\n".join(badge_list)
        
        embed.set_footer(text=f"Total: {len(user_badges)} badge{'s' if len(user_badges) > 1 else ''}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='givebadge')
    @commands.has_permissions(administrator=True)
    async def give_badge(self, ctx, member: discord.Member, badge: str):
        """🎁 Donner un badge à un utilisateur"""
        
        if badge.lower() not in self.badges:
            available_badges = ", ".join(self.badges.keys())
            return await ctx.send(f"❌ Badge invalide ! Disponibles: {available_badges}")
        
        badge = badge.lower()
        
        # Vérifier si l'utilisateur a déjà ce badge
        user_badges = self.get_user_badges(member.id, ctx.guild.id)
        if badge in user_badges:
            return await ctx.send(f"❌ {member.display_name} possède déjà ce badge !")
        
        # Ajouter le badge
        self.add_user_badge(member.id, ctx.guild.id, badge)
        
        badge_info = self.badges[badge]
        
        embed = discord.Embed(
            title="🎁 Badge accordé",
            description=f"{member.mention} a reçu le badge **{badge_info['name']}** {badge_info['emoji']}",
            color=0x00ff41
        )
        
        embed.add_field(name="Description", value=badge_info['description'], inline=False)
        embed.add_field(name="Accordé par", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
        # Notifier l'utilisateur en privé
        try:
            dm_embed = discord.Embed(
                title=f"🎁 Nouveau badge sur {ctx.guild.name}",
                description=f"Vous avez reçu le badge **{badge_info['name']}** {badge_info['emoji']}",
                color=0x00ff41
            )
            dm_embed.add_field(name="Description", value=badge_info['description'], inline=False)
            
            await member.send(embed=dm_embed)
        except:
            pass  # Ignorer si les DM sont fermés
    
    @commands.command(name='removebadge')
    @commands.has_permissions(administrator=True)
    async def remove_badge(self, ctx, member: discord.Member, badge: str):
        """🗑️ Retirer un badge à un utilisateur"""
        
        if badge.lower() not in self.badges:
            return await ctx.send("❌ Badge invalide !")
        
        badge = badge.lower()
        
        # Vérifier si l'utilisateur a ce badge
        user_badges = self.get_user_badges(member.id, ctx.guild.id)
        if badge not in user_badges:
            return await ctx.send(f"❌ {member.display_name} ne possède pas ce badge !")
        
        # Retirer le badge
        self.remove_user_badge(member.id, ctx.guild.id, badge)
        
        badge_info = self.badges[badge]
        
        embed = discord.Embed(
            title="🗑️ Badge retiré",
            description=f"Le badge **{badge_info['name']}** {badge_info['emoji']} a été retiré à {member.mention}",
            color=0xff4757
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='avatar')
    async def show_avatar(self, ctx, member: discord.Member = None):
        """🖼️ Voir l'avatar d'un utilisateur"""
        
        target = member or ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ Avatar de {target.display_name}",
            color=target.color if target.color != discord.Color.default() else 0x3498db
        )
        
        avatar_url = target.avatar.url if target.avatar else target.default_avatar.url
        embed.set_image(url=avatar_url)
        
        # Liens de téléchargement
        embed.add_field(
            name="📥 Télécharger",
            value=f"[PNG]({avatar_url}?size=1024) | [JPG]({avatar_url.replace('.png', '.jpg')}?size=1024) | [WEBP]({avatar_url.replace('.png', '.webp')}?size=1024)",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='status', aliases=['statut'])
    async def custom_status(self, ctx, *, status: str = None):
        """📝 Définir un statut personnalisé"""
        
        if not status:
            # Supprimer le statut
            self.update_user_profile(ctx.author.id, ctx.guild.id, {'status': None})
            return await ctx.send("✅ Statut personnalisé supprimé !")
        
        if len(status) > 100:
            return await ctx.send("❌ Le statut ne peut pas dépasser 100 caractères !")
        
        self.update_user_profile(ctx.author.id, ctx.guild.id, {'status': status})
        
        embed = discord.Embed(
            title="✅ Statut mis à jour",
            description=f"**Nouveau statut:** {status}",
            color=0x00ff41
        )
        
        await ctx.send(embed=embed)
    
    @commands.group(name='theme', invoke_without_command=True)
    async def theme_group(self, ctx):
        """🎭 Commandes de thèmes"""
        
        embed = discord.Embed(
            title="🎭 Thèmes disponibles",
            description="Utilisez `theme preview <nom>` pour voir un aperçu",
            color=0x3498db
        )
        
        for theme_name, theme_data in self.themes.items():
            embed.add_field(
                name=theme_name.title(),
                value=f"BG: {theme_data['bg']}\nAccent: {theme_data['accent']}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @theme_group.command(name='preview')
    async def theme_preview(self, ctx, theme: str):
        """👁️ Aperçu d'un thème"""
        
        if theme.lower() not in self.themes:
            return await ctx.send("❌ Thème invalide !")
        
        theme_data = self.themes[theme.lower()]
        
        embed = discord.Embed(
            title=f"🎭 Aperçu du thème: {theme}",
            description="Voici à quoi ressemblera votre profil avec ce thème",
            color=int(theme_data['accent'].replace('#', ''), 16)
        )
        
        # Créer une image d'aperçu
        preview_image = await self.create_theme_preview(theme.lower(), ctx.author)
        file = discord.File(preview_image, filename='theme_preview.png')
        
        embed.set_image(url="attachment://theme_preview.png")
        
        await ctx.send(embed=embed, file=file)
    
    async def create_profile_card(self, user: discord.Member, profile_data: dict, guild: discord.Guild):
        """Créer une carte de profil personnalisée"""
        
        # Dimensions de la carte
        width, height = 800, 400
        
        # Créer l'image de base
        img = Image.new('RGB', (width, height), color=profile_data.get('bg_color', '#2c3e50'))
        draw = ImageDraw.Draw(img)
        
        # Image de fond personnalisée
        if profile_data.get('background'):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(profile_data['background']) as resp:
                        if resp.status == 200:
                            bg_data = await resp.read()
                            bg_img = Image.open(io.BytesIO(bg_data))
                            bg_img = bg_img.resize((width, height))
                            bg_img = bg_img.filter(ImageFilter.GaussianBlur(2))
                            
                            # Overlay semi-transparent
                            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 128))
                            img = Image.alpha_composite(bg_img.convert('RGBA'), overlay)
            except:
                pass  # Utiliser la couleur de fond par défaut
        
        # Avatar de l'utilisateur
        try:
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(str(avatar_url)) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        avatar_img = Image.open(io.BytesIO(avatar_data))
                        avatar_img = avatar_img.resize((120, 120))
                        
                        # Créer un masque circulaire
                        mask = Image.new('L', (120, 120), 0)
                        mask_draw = ImageDraw.Draw(mask)
                        mask_draw.ellipse((0, 0, 120, 120), fill=255)
                        
                        # Appliquer le masque
                        avatar_img.putalpha(mask)
                        img.paste(avatar_img, (50, 50), avatar_img)
        except:
            pass  # Ignorer si impossible de charger l'avatar
        
        # Informations utilisateur
        try:
            # Utiliser une police par défaut
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = font_medium = font_small = ImageFont.load_default()
        
        # Nom d'utilisateur
        draw.text((200, 60), user.display_name, font=font_large, fill='white')
        
        # Discriminator et ID
        draw.text((200, 100), f"#{user.discriminator} • ID: {user.id}", font=font_small, fill='#b0b0b0')
        
        # Bio
        if profile_data.get('bio'):
            bio_lines = profile_data['bio'][:100].split('\n')
            y_offset = 140
            for line in bio_lines[:3]:  # Max 3 lignes
                draw.text((200, y_offset), line, font=font_small, fill='white')
                y_offset += 20
        
        # Statistiques
        balance = self.bot.db.get_user_balance(user.id, guild.id)
        level_data = self.bot.db.get_user_level(user.id, guild.id)
        
        stats_y = 250
        draw.text((50, stats_y), f"💰 {balance:,} ArsenalCoins", font=font_medium, fill='#f1c40f')
        draw.text((50, stats_y + 30), f"⭐ Niveau {level_data['level']}", font=font_medium, fill='#3498db')
        draw.text((50, stats_y + 60), f"🏆 {level_data['xp']:,} XP", font=font_medium, fill='#e74c3c')
        
        # Badges
        user_badges = self.get_user_badges(user.id, guild.id)
        if user_badges:
            badge_text = " ".join([self.badges[badge]['emoji'] for badge in user_badges[:5] if badge in self.badges])
            draw.text((400, stats_y), f"Badges: {badge_text}", font=font_medium, fill='white')
        
        # Convertir en bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    async def create_theme_preview(self, theme: str, user: discord.Member):
        """Créer un aperçu de thème"""
        
        theme_data = self.themes[theme]
        
        # Créer une image d'aperçu simple
        width, height = 400, 200
        bg_color = theme_data['bg']
        accent_color = theme_data['accent']
        
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Dessiner des éléments de thème
        draw.rectangle([20, 20, width-20, height-20], outline=accent_color, width=3)
        draw.text((40, 40), f"Thème: {theme.title()}", fill='white')
        draw.text((40, 70), f"Utilisateur: {user.display_name}", fill='white')
        draw.text((40, 100), f"Couleur d'accent: {accent_color}", fill=accent_color)
        
        # Convertir en bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def get_user_profile(self, user_id: int, guild_id: int) -> dict:
        """Récupérer le profil d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bio, color, theme, background, status
                FROM user_profiles
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'bio': result[0],
                    'color': result[1] or 0x3498db,
                    'theme': result[2] or 'default',
                    'background': result[3],
                    'status': result[4]
                }
            
            return {'color': 0x3498db, 'theme': 'default'}
    
    def update_user_profile(self, user_id: int, guild_id: int, data: dict):
        """Mettre à jour le profil d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Insérer ou mettre à jour
            cursor.execute('''
                INSERT OR IGNORE INTO user_profiles (user_id, guild_id)
                VALUES (?, ?)
            ''', (user_id, guild_id))
            
            # Mettre à jour les champs fournis
            for key, value in data.items():
                cursor.execute(f'''
                    UPDATE user_profiles
                    SET {key} = ?
                    WHERE user_id = ? AND guild_id = ?
                ''', (value, user_id, guild_id))
            
            conn.commit()
    
    def get_user_badges(self, user_id: int, guild_id: int) -> List[str]:
        """Récupérer les badges d'un utilisateur"""
        with sqlite3.connect(self.bot.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT badges FROM user_profiles
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            result = cursor.fetchone()
            
            if result and result[0]:
                try:
                    return json.loads(result[0])
                except:
                    return []
            
            return []
    
    def add_user_badge(self, user_id: int, guild_id: int, badge: str):
        """Ajouter un badge à un utilisateur"""
        current_badges = self.get_user_badges(user_id, guild_id)
        
        if badge not in current_badges:
            current_badges.append(badge)
            self.update_user_profile(user_id, guild_id, {'badges': json.dumps(current_badges)})
    
    def remove_user_badge(self, user_id: int, guild_id: int, badge: str):
        """Retirer un badge à un utilisateur"""
        current_badges = self.get_user_badges(user_id, guild_id)
        
        if badge in current_badges:
            current_badges.remove(badge)
            self.update_user_profile(user_id, guild_id, {'badges': json.dumps(current_badges)})

def setup(bot):
    bot.add_cog(PersonalizationModule(bot))
