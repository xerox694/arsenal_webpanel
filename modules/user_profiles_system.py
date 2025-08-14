#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👤 ARSENAL V4 - SYSTÈME DE PROFILS UTILISATEURS ULTRA-AVANCÉ
Personnalisation complète : styles d'écriture, thèmes, préférences, statistiques
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.logger import log

class UserProfileSystem:
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/user_profiles.json"
        self.profiles = {}
        self.load_profiles()
        
    def load_profiles(self):
        """Charge les profils utilisateurs"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
                log.info("👤 Profils utilisateurs chargés")
            except Exception as e:
                log.error(f"❌ Erreur chargement profils: {e}")
                self.profiles = {}
        else:
            self.profiles = {}
    
    def save_profiles(self):
        """Sauvegarde les profils utilisateurs"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.profiles, f, indent=4, ensure_ascii=False)
            log.info("💾 Profils utilisateurs sauvegardés")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde profils: {e}")
    
    def get_user_profile(self, user_id: int) -> dict:
        """Récupère le profil d'un utilisateur"""
        user_id = str(user_id)
        if user_id not in self.profiles:
            self.profiles[user_id] = self.get_default_profile()
            self.save_profiles()
        return self.profiles[user_id]
    
    def update_user_profile(self, user_id: int, profile_data: dict):
        """Met à jour le profil d'un utilisateur"""
        user_id = str(user_id)
        self.profiles[user_id] = profile_data
        self.save_profiles()
    
    def get_default_profile(self) -> dict:
        """Profil par défaut"""
        return {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            
            # 🎨 Styles d'écriture personnalisés
            "writing_style": {
                "enabled": False,
                "style_name": "normal",
                "text_transforms": {
                    "uppercase": False,           # TEXTE EN MAJUSCULES
                    "lowercase": False,           # texte en minuscules
                    "title_case": False,          # Texte En Titre
                    "alternating_case": False,    # tExTe AlTeRnE
                    "leetspeak": False,           # 73x73 3n 1337
                    "uwu_mode": False,            # OwO texts becomes uwu
                    "zalgo_text": False,          # T̴e̷x̸t̵e̶ ̷Z̴a̶l̵g̶o̸
                    "reverse_text": False,        # etxet esrevni
                    "bubble_text": False,         # Ⓣⓔⓧⓣⓔ ⓑⓤⓛⓛⓔⓢ
                    "bold_text": False,           # 𝐓𝐞𝐱𝐭𝐞 𝐞𝐧 𝐠𝐫𝐚𝐬
                    "italic_text": False,         # 𝑇𝑒𝑥𝑡𝑒 𝑒𝑛 𝑖𝑡𝑎𝑙𝑖𝑞𝑢𝑒
                    "strikethrough": False,       # ~~Texte barré~~
                    "underline": False,           # __Texte souligné__
                    "spoiler": False              # ||Texte caché||
                },
                "emoji_style": {
                    "auto_react": False,          # Réactions automatiques
                    "emoji_suffix": "",           # Emoji à la fin des messages
                    "emoji_prefix": "",           # Emoji au début des messages
                    "random_reactions": False,    # Réactions aléatoires
                    "custom_reactions": []        # Liste d'emojis personnalisés
                },
                "message_formatting": {
                    "add_signature": False,       # Signature automatique
                    "signature_text": "",         # Texte de signature
                    "add_timestamp": False,       # Horodatage automatique
                    "colored_text": False,        # Texte coloré (si possible)
                    "ascii_art_mode": False,      # Art ASCII automatique
                    "quote_style": "normal"       # Style de citation
                }
            },
            
            # 🎭 Thèmes et apparence
            "theme": {
                "color_scheme": "default",        # Schéma de couleurs
                "embed_color": "#7289da",         # Couleur des embeds personnalisés
                "profile_banner": None,           # URL bannière de profil
                "profile_description": "",        # Description personnalisée
                "status_message": "",             # Message de statut
                "custom_title": "",               # Titre personnalisé
                "badges": []                      # Badges collectés
            },
            
            # 🔧 Préférences générales
            "preferences": {
                "language": "fr",                 # Langue préférée
                "timezone": "Europe/Paris",       # Fuseau horaire
                "date_format": "DD/MM/YYYY",      # Format de date
                "time_format": "24h",             # Format d'heure
                "privacy_level": "public",        # Niveau de confidentialité
                "dm_notifications": True,         # Notifications DM
                "mention_notifications": True,    # Notifications mentions
                "auto_delete_commands": False,    # Suppression auto des commandes
                "compact_mode": False,            # Mode compact
                "show_typing": True,              # Afficher "en train d'écrire"
                "auto_translate": False,          # Traduction automatique
                "profanity_filter": True          # Filtre de vulgarité personnel
            },
            
            # 📊 Statistiques personnelles
            "statistics": {
                "messages_sent": 0,               # Messages envoyés
                "commands_used": 0,               # Commandes utilisées
                "voice_time": 0,                  # Temps en vocal (secondes)
                "reactions_given": 0,             # Réactions données
                "reactions_received": 0,          # Réactions reçues
                "favorite_channels": {},          # Salons favoris (usage)
                "activity_hours": {},             # Heures d'activité
                "first_message": None,            # Premier message
                "last_activity": None,            # Dernière activité
                "streak_days": 0,                 # Jours consécutifs d'activité
                "achievements": []                # Succès débloqués
            },
            
            # 🎮 Paramètres de jeu et économie
            "gaming": {
                "auto_daily": False,              # Récupération automatique daily
                "investment_alerts": True,        # Alertes d'investissement
                "gambling_limit": 1000,           # Limite de jeu par jour
                "favorite_games": [],             # Jeux favoris
                "gaming_quotes": [],              # Citations de jeu
                "achievement_notifications": True # Notifications de succès
            },
            
            # 🛡️ Sécurité et modération
            "security": {
                "two_factor_auth": False,         # Authentification 2FA
                "login_alerts": True,             # Alertes de connexion
                "suspicious_activity": True,      # Détection d'activité suspecte
                "auto_backup": True,              # Sauvegarde automatique
                "data_retention": 365,            # Rétention des données (jours)
                "share_statistics": True          # Partager les statistiques
            },
            
            # 🎵 Préférences multimédia
            "media": {
                "auto_embed": True,               # Intégration automatique des liens
                "image_previews": True,           # Aperçus d'images
                "video_autoplay": False,          # Lecture automatique vidéos
                "music_notifications": True,      # Notifications musique
                "gif_autoplay": True,             # Lecture automatique GIFs
                "media_quality": "high"           # Qualité média préférée
            },
            
            # 🔗 Intégrations externes
            "integrations": {
                "github_username": "",            # Nom d'utilisateur GitHub
                "twitter_handle": "",             # Handle Twitter
                "twitch_channel": "",             # Chaîne Twitch
                "youtube_channel": "",            # Chaîne YouTube
                "steam_profile": "",              # Profil Steam
                "sync_status": False,             # Synchroniser le statut
                "cross_platform_notifications": False # Notifications cross-platform
            }
        }
    
    def get_writing_styles(self) -> Dict[str, dict]:
        """Styles d'écriture prédéfinis"""
        return {
            "normal": {
                "name": "📝 Normal",
                "description": "Style d'écriture standard",
                "transforms": {}
            },
            "casual": {
                "name": "😎 Décontracté", 
                "description": "Style décontracté avec emojis",
                "transforms": {
                    "emoji_suffix": " 😊",
                    "lowercase": True
                }
            },
            "professional": {
                "name": "💼 Professionnel",
                "description": "Style formel et professionnel",
                "transforms": {
                    "title_case": True,
                    "add_signature": True,
                    "signature_text": "Cordialement"
                }
            },
            "gaming": {
                "name": "🎮 Gaming",
                "description": "Style gaming avec réactions",
                "transforms": {
                    "auto_react": True,
                    "custom_reactions": ["🎮", "🔥", "💯", "⚡"],
                    "leetspeak": True
                }
            },
            "uwu": {
                "name": "🐱 UwU Mode",
                "description": "OwO what's this? UwU style",
                "transforms": {
                    "uwu_mode": True,
                    "emoji_suffix": " uwu"
                }
            },
            "aesthetic": {
                "name": "✨ Esthétique",
                "description": "Style esthétique avec texte spécial",
                "transforms": {
                    "bubble_text": True,
                    "emoji_prefix": "✨ ",
                    "emoji_suffix": " ✨"
                }
            },
            "hacker": {
                "name": "💻 Hacker",
                "description": "Style hacker en 1337 speak",
                "transforms": {
                    "leetspeak": True,
                    "lowercase": True,
                    "emoji_prefix": "💻 "
                }
            },
            "royal": {
                "name": "👑 Royal",
                "description": "Style royal et majestueux",
                "transforms": {
                    "bold_text": True,
                    "title_case": True,
                    "add_signature": True,
                    "signature_text": "👑 Mes respects"
                }
            },
            "mysterious": {
                "name": "🌙 Mystérieux",
                "description": "Style mystérieux avec spoilers",
                "transforms": {
                    "spoiler": True,
                    "emoji_prefix": "🌙 ",
                    "italic_text": True
                }
            },
            "chaotic": {
                "name": "🌪️ Chaotique",
                "description": "Style chaotique et imprévisible",
                "transforms": {
                    "alternating_case": True,
                    "random_reactions": True,
                    "zalgo_text": True
                }
            }
        }
    
    def apply_writing_style(self, text: str, user_profile: dict) -> str:
        """Applique le style d'écriture à un texte"""
        if not user_profile["writing_style"]["enabled"]:
            return text
        
        transforms = user_profile["writing_style"]["text_transforms"]
        
        # Transformations de base
        if transforms.get("uppercase"):
            text = text.upper()
        elif transforms.get("lowercase"):
            text = text.lower()
        elif transforms.get("title_case"):
            text = text.title()
        elif transforms.get("alternating_case"):
            text = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        
        # Transformations spéciales
        if transforms.get("reverse_text"):
            text = text[::-1]
        
        if transforms.get("leetspeak"):
            text = self.convert_to_leetspeak(text)
        
        if transforms.get("uwu_mode"):
            text = self.convert_to_uwu(text)
        
        if transforms.get("bubble_text"):
            text = self.convert_to_bubble_text(text)
        
        if transforms.get("bold_text"):
            text = self.convert_to_bold_unicode(text)
        
        if transforms.get("italic_text"):
            text = self.convert_to_italic_unicode(text)
        
        # Formatage Discord
        if transforms.get("strikethrough"):
            text = f"~~{text}~~"
        
        if transforms.get("underline"):
            text = f"__{text}__"
        
        if transforms.get("spoiler"):
            text = f"||{text}||"
        
        # Ajout de préfixes/suffixes
        emoji_formatting = user_profile["writing_style"]["emoji_style"]
        
        if emoji_formatting.get("emoji_prefix"):
            text = emoji_formatting["emoji_prefix"] + text
        
        if emoji_formatting.get("emoji_suffix"):
            text = text + emoji_formatting["emoji_suffix"]
        
        # Signature
        message_formatting = user_profile["writing_style"]["message_formatting"]
        if message_formatting.get("add_signature") and message_formatting.get("signature_text"):
            text += f"\n\n{message_formatting['signature_text']}"
        
        # Horodatage
        if message_formatting.get("add_timestamp"):
            timestamp = datetime.now().strftime("%H:%M")
            text += f" `[{timestamp}]`"
        
        return text
    
    def convert_to_leetspeak(self, text: str) -> str:
        """Convertit le texte en leet speak"""
        leet_map = {
            'a': '4', 'A': '4',
            'e': '3', 'E': '3', 
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            't': '7', 'T': '7',
            'l': '1', 'L': '1',
            'g': '9', 'G': '9'
        }
        return ''.join(leet_map.get(c, c) for c in text)
    
    def convert_to_uwu(self, text: str) -> str:
        """Convertit le texte en UwU speak"""
        text = text.replace('r', 'w').replace('R', 'W')
        text = text.replace('l', 'w').replace('L', 'W')
        text = text.replace('na', 'nya').replace('Na', 'Nya')
        text = text.replace('ne', 'nye').replace('Ne', 'Nye')
        text = text.replace('ni', 'nyi').replace('Ni', 'Nyi')
        text = text.replace('no', 'nyo').replace('No', 'Nyo')
        text = text.replace('nu', 'nyu').replace('Nu', 'Nyu')
        return text
    
    def convert_to_bubble_text(self, text: str) -> str:
        """Convertit le texte en bubble text"""
        bubble_map = {
            'A': 'Ⓐ', 'B': 'Ⓑ', 'C': 'Ⓒ', 'D': 'Ⓓ', 'E': 'Ⓔ', 'F': 'Ⓕ', 'G': 'Ⓖ', 'H': 'Ⓗ',
            'I': 'Ⓘ', 'J': 'Ⓙ', 'K': 'Ⓚ', 'L': 'Ⓛ', 'M': 'Ⓜ', 'N': 'Ⓝ', 'O': 'Ⓞ', 'P': 'Ⓟ',
            'Q': 'Ⓠ', 'R': 'Ⓡ', 'S': 'Ⓢ', 'T': 'Ⓣ', 'U': 'Ⓤ', 'V': 'Ⓥ', 'W': 'Ⓦ', 'X': 'Ⓧ',
            'Y': 'Ⓨ', 'Z': 'Ⓩ',
            'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ', 'f': 'ⓕ', 'g': 'ⓖ', 'h': 'ⓗ',
            'i': 'ⓘ', 'j': 'ⓙ', 'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ', 'o': 'ⓞ', 'p': 'ⓟ',
            'q': 'ⓠ', 'r': 'ⓡ', 's': 'ⓢ', 't': 'ⓣ', 'u': 'ⓤ', 'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ',
            'y': 'ⓨ', 'z': 'ⓩ',
            '0': '⓪', '1': '①', '2': '②', '3': '③', '4': '④', '5': '⑤', '6': '⑥', '7': '⑦',
            '8': '⑧', '9': '⑨'
        }
        return ''.join(bubble_map.get(c, c) for c in text)
    
    def convert_to_bold_unicode(self, text: str) -> str:
        """Convertit le texte en gras Unicode"""
        bold_map = {
            'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇',
            'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏',
            'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗',
            'Y': '𝐘', 'Z': '𝐙',
            'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡',
            'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩',
            'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱',
            'y': '𝐲', 'z': '𝐳'
        }
        return ''.join(bold_map.get(c, c) for c in text)
    
    def convert_to_italic_unicode(self, text: str) -> str:
        """Convertit le texte en italique Unicode"""
        italic_map = {
            'A': '𝐴', 'B': '𝐵', 'C': '𝐶', 'D': '𝐷', 'E': '𝐸', 'F': '𝐹', 'G': '𝐺', 'H': '𝐻',
            'I': '𝐼', 'J': '𝐽', 'K': '𝐾', 'L': '𝐿', 'M': '𝑀', 'N': '𝑁', 'O': '𝑂', 'P': '𝑃',
            'Q': '𝑄', 'R': '𝑅', 'S': '𝑆', 'T': '𝑇', 'U': '𝑈', 'V': '𝑉', 'W': '𝑊', 'X': '𝑋',
            'Y': '𝑌', 'Z': '𝑍',
            'a': '𝑎', 'b': '𝑏', 'c': '𝑐', 'd': '𝑑', 'e': '𝑒', 'f': '𝑓', 'g': '𝑔', 'h': 'ℎ',
            'i': '𝑖', 'j': '𝑗', 'k': '𝑘', 'l': '𝑙', 'm': '𝑚', 'n': '𝑛', 'o': '𝑜', 'p': '𝑝',
            'q': '𝑞', 'r': '𝑟', 's': '𝑠', 't': '𝑡', 'u': '𝑢', 'v': '𝑣', 'w': '𝑤', 'x': '𝑥',
            'y': '𝑦', 'z': '𝑧'
        }
        return ''.join(italic_map.get(c, c) for c in text)
    
    async def update_user_statistics(self, user_id: int, stat_type: str, increment: int = 1):
        """Met à jour les statistiques d'un utilisateur"""
        profile = self.get_user_profile(user_id)
        profile["statistics"][stat_type] = profile["statistics"].get(stat_type, 0) + increment
        profile["statistics"]["last_activity"] = datetime.now().isoformat()
        self.update_user_profile(user_id, profile)
    
    async def check_achievements(self, user_id: int) -> List[str]:
        """Vérifie les nouveaux succès débloqués"""
        profile = self.get_user_profile(user_id)
        stats = profile["statistics"]
        achievements = profile["statistics"]["achievements"]
        new_achievements = []
        
        # Définition des succès
        achievement_list = {
            "first_steps": {
                "name": "👶 Premiers Pas",
                "description": "Envoyer votre premier message",
                "condition": lambda s: s["messages_sent"] >= 1
            },
            "chatterbox": {
                "name": "💬 Bavard",
                "description": "Envoyer 100 messages",
                "condition": lambda s: s["messages_sent"] >= 100
            },
            "commander": {
                "name": "⚡ Commandant",
                "description": "Utiliser 25 commandes",
                "condition": lambda s: s["commands_used"] >= 25
            },
            "social_butterfly": {
                "name": "🦋 Papillon Social",
                "description": "Recevoir 50 réactions",
                "condition": lambda s: s["reactions_received"] >= 50
            },
            "voice_lover": {
                "name": "🎤 Amateur de Vocal",
                "description": "Passer 1 heure en vocal",
                "condition": lambda s: s["voice_time"] >= 3600
            },
            "night_owl": {
                "name": "🦉 Oiseau de Nuit",
                "description": "Être actif après 2h du matin",
                "condition": lambda s: any(int(hour) >= 2 and int(hour) <= 6 for hour in s.get("activity_hours", {}).keys())
            },
            "early_bird": {
                "name": "🐦 Lève-Tôt",
                "description": "Être actif avant 6h du matin",
                "condition": lambda s: any(int(hour) <= 6 for hour in s.get("activity_hours", {}).keys())
            },
            "consistent": {
                "name": "📅 Régulier",
                "description": "7 jours consécutifs d'activité",
                "condition": lambda s: s["streak_days"] >= 7
            }
        }
        
        # Vérifier chaque succès
        for achievement_id, achievement in achievement_list.items():
            if achievement_id not in achievements and achievement["condition"](stats):
                achievements.append(achievement_id)
                new_achievements.append(achievement["name"])
        
        if new_achievements:
            self.update_user_profile(user_id, profile)
        
        return new_achievements

class ProfileConfigView(discord.ui.View):
    """Interface de configuration du profil utilisateur"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(timeout=300)
        self.user = user
        self.profile_system = profile_system
        self.profile = profile_system.get_user_profile(user.id)
    
    @discord.ui.select(
        placeholder="📋 Choisissez une catégorie à configurer...",
        options=[
            discord.SelectOption(
                label="🎨 Style d'écriture",
                description="Personnalisez votre façon d'écrire",
                emoji="🎨",
                value="writing_style"
            ),
            discord.SelectOption(
                label="🎭 Thème et apparence",
                description="Couleurs, bannière, badges",
                emoji="🎭",
                value="theme"
            ),
            discord.SelectOption(
                label="🔧 Préférences générales",
                description="Langue, notifications, confidentialité",
                emoji="🔧",
                value="preferences"
            ),
            discord.SelectOption(
                label="📊 Statistiques",
                description="Voir vos statistiques et succès",
                emoji="📊",
                value="statistics"
            ),
            discord.SelectOption(
                label="🎮 Paramètres de jeu",
                description="Économie, jeux, alertes",
                emoji="🎮",
                value="gaming"
            )
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier le profil de quelqu'un d'autre", ephemeral=True)
            return
        
        category = select.values[0]
        
        if category == "writing_style":
            view = WritingStyleConfigView(self.user, self.profile_system)
            embed = discord.Embed(
                title="🎨 Configuration du Style d'Écriture",
                description="Personnalisez votre façon d'écrire et d'apparaître sur le serveur",
                color=discord.Color.purple()
            )
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif category == "theme":
            view = ThemeConfigView(self.user, self.profile_system)
            embed = discord.Embed(
                title="🎭 Configuration du Thème",
                description="Personnalisez votre apparence et vos couleurs",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif category == "preferences":
            view = PreferencesConfigView(self.user, self.profile_system)
            embed = discord.Embed(
                title="🔧 Préférences Générales",
                description="Configurez vos préférences système",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif category == "statistics":
            await self.show_statistics(interaction)
        
        elif category == "gaming":
            view = GamingConfigView(self.user, self.profile_system)
            embed = discord.Embed(
                title="🎮 Paramètres de Jeu",
                description="Configurez vos préférences de jeu et d'économie",
                color=discord.Color.gold()
            )
            await interaction.response.edit_message(embed=embed, view=view)
    
    async def show_statistics(self, interaction: discord.Interaction):
        """Affiche les statistiques de l'utilisateur"""
        stats = self.profile["statistics"]
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {self.user.display_name}",
            color=discord.Color.blue()
        )
        
        # Statistiques générales
        embed.add_field(
            name="💬 Activité",
            value=(
                f"**Messages:** {stats['messages_sent']:,}\n"
                f"**Commandes:** {stats['commands_used']:,}\n"
                f"**Temps vocal:** {stats['voice_time']//3600}h {(stats['voice_time']%3600)//60}m"
            ),
            inline=True
        )
        
        # Interactions sociales
        embed.add_field(
            name="👥 Social",
            value=(
                f"**Réactions données:** {stats['reactions_given']:,}\n"
                f"**Réactions reçues:** {stats['reactions_received']:,}\n"
                f"**Jours consécutifs:** {stats['streak_days']}"
            ),
            inline=True
        )
        
        # Succès
        achievements = stats.get("achievements", [])
        if achievements:
            achievement_names = []
            styles = self.profile_system.get_writing_styles()  # Pour récupérer les noms des succès
            # Ici on afficherait les vrais noms des succès
            embed.add_field(
                name="🏆 Succès débloqués",
                value=f"**{len(achievements)}** succès débloqués",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)

class WritingStyleConfigView(discord.ui.View):
    """Interface de configuration du style d'écriture"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(timeout=300)
        self.user = user
        self.profile_system = profile_system
        self.profile = profile_system.get_user_profile(user.id)
    
    @discord.ui.select(
        placeholder="🎨 Choisissez un style d'écriture prédéfini...",
        options=[
            discord.SelectOption(label="📝 Normal", description="Style standard", value="normal"),
            discord.SelectOption(label="😎 Décontracté", description="Style cool avec emojis", value="casual"),
            discord.SelectOption(label="💼 Professionnel", description="Style formel", value="professional"),
            discord.SelectOption(label="🎮 Gaming", description="Style gaming", value="gaming"),
            discord.SelectOption(label="🐱 UwU Mode", description="OwO what's this?", value="uwu"),
            discord.SelectOption(label="✨ Esthétique", description="Style esthétique", value="aesthetic"),
            discord.SelectOption(label="💻 Hacker", description="1337 speak", value="hacker"),
            discord.SelectOption(label="👑 Royal", description="Style majestueux", value="royal"),
            discord.SelectOption(label="🌙 Mystérieux", description="Style énigmatique", value="mysterious"),
            discord.SelectOption(label="🌪️ Chaotique", description="Style imprévisible", value="chaotic")
        ]
    )
    async def select_style(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier le profil de quelqu'un d'autre", ephemeral=True)
            return
        
        style_name = select.values[0]
        styles = self.profile_system.get_writing_styles()
        selected_style = styles[style_name]
        
        # Appliquer le style
        self.profile["writing_style"]["enabled"] = True
        self.profile["writing_style"]["style_name"] = style_name
        
        # Réinitialiser les transformations
        for key in self.profile["writing_style"]["text_transforms"]:
            self.profile["writing_style"]["text_transforms"][key] = False
        for key in self.profile["writing_style"]["emoji_style"]:
            if isinstance(self.profile["writing_style"]["emoji_style"][key], bool):
                self.profile["writing_style"]["emoji_style"][key] = False
            elif isinstance(self.profile["writing_style"]["emoji_style"][key], str):
                self.profile["writing_style"]["emoji_style"][key] = ""
            elif isinstance(self.profile["writing_style"]["emoji_style"][key], list):
                self.profile["writing_style"]["emoji_style"][key] = []
        
        # Appliquer les transformations du style choisi
        transforms = selected_style.get("transforms", {})
        for key, value in transforms.items():
            if key in self.profile["writing_style"]["text_transforms"]:
                self.profile["writing_style"]["text_transforms"][key] = value
            elif key in self.profile["writing_style"]["emoji_style"]:
                self.profile["writing_style"]["emoji_style"][key] = value
            elif key in self.profile["writing_style"]["message_formatting"]:
                self.profile["writing_style"]["message_formatting"][key] = value
        
        self.profile_system.update_user_profile(self.user.id, self.profile)
        
        # Test du style
        test_text = "Voici un exemple de texte avec votre nouveau style !"
        styled_text = self.profile_system.apply_writing_style(test_text, self.profile)
        
        embed = discord.Embed(
            title=f"✅ Style appliqué : {selected_style['name']}",
            description=selected_style['description'],
            color=discord.Color.green()
        )
        embed.add_field(
            name="📝 Aperçu",
            value=f"**Avant :** {test_text}\n**Après :** {styled_text}",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔧 Configuration avancée", style=discord.ButtonStyle.secondary)
    async def advanced_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier le profil de quelqu'un d'autre", ephemeral=True)
            return
        
        modal = AdvancedWritingStyleModal(self.user, self.profile_system)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="❌ Désactiver le style", style=discord.ButtonStyle.danger)
    async def disable_style(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier le profil de quelqu'un d'autre", ephemeral=True)
            return
        
        self.profile["writing_style"]["enabled"] = False
        self.profile_system.update_user_profile(self.user.id, self.profile)
        
        embed = discord.Embed(
            title="❌ Style d'écriture désactivé",
            description="Vos messages reviendront à leur forme normale",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=self)

class AdvancedWritingStyleModal(discord.ui.Modal):
    """Modal pour la configuration avancée du style d'écriture"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(title="🔧 Configuration Avancée du Style")
        self.user = user
        self.profile_system = profile_system
    
    emoji_prefix = discord.ui.TextInput(
        label="Emoji au début des messages",
        placeholder="Ex: ✨ ou 🎮 (laissez vide pour désactiver)",
        required=False,
        max_length=10
    )
    
    emoji_suffix = discord.ui.TextInput(
        label="Emoji à la fin des messages", 
        placeholder="Ex: 😊 ou uwu (laissez vide pour désactiver)",
        required=False,
        max_length=10
    )
    
    signature = discord.ui.TextInput(
        label="Signature automatique",
        placeholder="Ex: Cordialement, - Mon pseudo (laissez vide pour désactiver)",
        required=False,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        profile = self.profile_system.get_user_profile(self.user.id)
        
        # Mettre à jour les paramètres
        profile["writing_style"]["emoji_style"]["emoji_prefix"] = self.emoji_prefix.value
        profile["writing_style"]["emoji_style"]["emoji_suffix"] = self.emoji_suffix.value
        
        if self.signature.value:
            profile["writing_style"]["message_formatting"]["add_signature"] = True
            profile["writing_style"]["message_formatting"]["signature_text"] = self.signature.value
        else:
            profile["writing_style"]["message_formatting"]["add_signature"] = False
            profile["writing_style"]["message_formatting"]["signature_text"] = ""
        
        profile["writing_style"]["enabled"] = True
        self.profile_system.update_user_profile(self.user.id, profile)
        
        # Test
        test_text = "Test de votre configuration personnalisée"
        styled_text = self.profile_system.apply_writing_style(test_text, profile)
        
        embed = discord.Embed(
            title="✅ Configuration avancée sauvegardée",
            description="Vos paramètres personnalisés ont été appliqués",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📝 Aperçu",
            value=f"**Résultat :** {styled_text}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ThemeConfigView(discord.ui.View):
    """Interface de configuration du thème"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(timeout=300)
        self.user = user
        self.profile_system = profile_system
        self.profile = profile_system.get_user_profile(user.id)

class PreferencesConfigView(discord.ui.View):
    """Interface de configuration des préférences"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(timeout=300)
        self.user = user
        self.profile_system = profile_system
        self.profile = profile_system.get_user_profile(user.id)

class GamingConfigView(discord.ui.View):
    """Interface de configuration des paramètres de jeu"""
    
    def __init__(self, user: discord.Member, profile_system: UserProfileSystem):
        super().__init__(timeout=300)
        self.user = user
        self.profile_system = profile_system
        self.profile = profile_system.get_user_profile(user.id)

# Commandes slash pour les profils utilisateurs
profile_group = app_commands.Group(name="profile", description="👤 Gestion de votre profil utilisateur personnalisé")

@profile_group.command(name="config", description="Configure votre profil utilisateur")
async def profile_config(interaction: discord.Interaction):
    profile_system = interaction.client.get_cog('UserProfileSystem')
    if not profile_system:
        await interaction.response.send_message("❌ Système de profils non chargé", ephemeral=True)
        return
    
    view = ProfileConfigView(interaction.user, profile_system)
    
    embed = discord.Embed(
        title=f"👤 Profil de {interaction.user.display_name}",
        description="Configurez votre profil utilisateur personnalisé",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🎨 Personnalisation disponible",
        value=(
            "• **Style d'écriture** - Transformez vos messages\n"
            "• **Thème et apparence** - Couleurs et visuels\n"
            "• **Préférences** - Langue, notifications, confidentialité\n"
            "• **Statistiques** - Vos données d'activité\n"
            "• **Paramètres de jeu** - Économie et jeux"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@profile_group.command(name="view", description="Affiche le profil d'un utilisateur")
@app_commands.describe(user="Utilisateur dont voir le profil (optionnel)")
async def profile_view(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    
    profile_system = interaction.client.get_cog('UserProfileSystem')
    if not profile_system:
        await interaction.response.send_message("❌ Système de profils non chargé", ephemeral=True)
        return
    
    profile = profile_system.get_user_profile(user.id)
    stats = profile["statistics"]
    
    embed = discord.Embed(
        title=f"👤 Profil de {user.display_name}",
        color=int(profile["theme"]["embed_color"].replace("#", ""), 16) if profile["theme"]["embed_color"] else discord.Color.blue()
    )
    
    # Informations de base
    if profile["theme"]["profile_description"]:
        embed.description = profile["theme"]["profile_description"]
    
    # Style d'écriture
    writing_style = profile["writing_style"]
    if writing_style["enabled"]:
        embed.add_field(
            name="🎨 Style d'écriture",
            value=f"**Actif:** {writing_style['style_name'].title()}",
            inline=True
        )
    
    # Statistiques
    embed.add_field(
        name="📊 Activité",
        value=(
            f"**Messages:** {stats['messages_sent']:,}\n"
            f"**Commandes:** {stats['commands_used']:,}\n"
            f"**Temps vocal:** {stats['voice_time']//3600}h"
        ),
        inline=True
    )
    
    # Succès
    achievements = stats.get("achievements", [])
    embed.add_field(
        name="🏆 Succès",
        value=f"{len(achievements)} débloqués",
        inline=True
    )
    
    # Badges
    if profile["theme"]["badges"]:
        embed.add_field(
            name="🎖️ Badges",
            value=" ".join(profile["theme"]["badges"]),
            inline=False
        )
    
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.set_footer(text=f"Profil créé le {datetime.fromisoformat(profile['created_at']).strftime('%d/%m/%Y')}")
    
    await interaction.response.send_message(embed=embed)

@profile_group.command(name="test_style", description="Teste votre style d'écriture avec un texte personnalisé")
@app_commands.describe(text="Texte à tester avec votre style")
async def test_style(interaction: discord.Interaction, text: str):
    profile_system = interaction.client.get_cog('UserProfileSystem')
    if not profile_system:
        await interaction.response.send_message("❌ Système de profils non chargé", ephemeral=True)
        return
    
    profile = profile_system.get_user_profile(interaction.user.id)
    
    if not profile["writing_style"]["enabled"]:
        await interaction.response.send_message("❌ Vous n'avez pas de style d'écriture activé", ephemeral=True)
        return
    
    styled_text = profile_system.apply_writing_style(text, profile)
    
    embed = discord.Embed(
        title="🧪 Test de style d'écriture",
        color=discord.Color.purple()
    )
    embed.add_field(name="📝 Texte original", value=text, inline=False)
    embed.add_field(name="🎨 Avec votre style", value=styled_text, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@profile_group.command(name="reset", description="Remet votre profil à zéro")
async def profile_reset(interaction: discord.Interaction):
    profile_system = interaction.client.get_cog('UserProfileSystem')
    if not profile_system:
        await interaction.response.send_message("❌ Système de profils non chargé", ephemeral=True)
        return
    
    # Demander confirmation
    embed = discord.Embed(
        title="⚠️ Confirmation de remise à zéro",
        description="Êtes-vous sûr de vouloir remettre votre profil à zéro ?\n\n**Cette action est irréversible et supprimera :**\n• Votre style d'écriture\n• Vos préférences\n• Vos statistiques\n• Vos succès",
        color=discord.Color.red()
    )
    
    class ConfirmResetView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
        
        @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != interaction.user.id:
                return
            
            # Réinitialiser le profil
            profile_system.profiles[str(interaction.user.id)] = profile_system.get_default_profile()
            profile_system.save_profiles()
            
            embed = discord.Embed(
                title="✅ Profil remis à zéro",
                description="Votre profil a été réinitialisé avec succès",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = discord.Embed(
                title="❌ Remise à zéro annulée",
                description="Votre profil n'a pas été modifié",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=None)
    
    await interaction.response.send_message(embed=embed, view=ConfirmResetView(), ephemeral=True)

class UserProfileCog(commands.Cog):
    """Cog pour le système de profils utilisateurs"""
    
    def __init__(self, bot):
        self.bot = bot
        self.profile_system = UserProfileSystem(bot)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour appliquer les styles et mettre à jour les stats"""
        if message.author.bot or not message.guild:
            return
        
        # Mettre à jour les statistiques
        await self.profile_system.update_user_statistics(message.author.id, "messages_sent")
        
        # Vérifier les nouveaux succès
        new_achievements = await self.profile_system.check_achievements(message.author.id)
        if new_achievements:
            embed = discord.Embed(
                title="🏆 Nouveau(x) Succès Débloqué(s) !",
                description="\n".join(f"✨ {achievement}" for achievement in new_achievements),
                color=discord.Color.gold()
            )
            try:
                await message.author.send(embed=embed)
            except:
                pass  # L'utilisateur a peut-être désactivé les DMs
    
    @commands.Cog.listener() 
    async def on_voice_state_update(self, member, before, after):
        """Suit le temps passé en vocal"""
        if member.bot:
            return
        
        # Si l'utilisateur rejoint un vocal
        if before.channel is None and after.channel is not None:
            profile = self.profile_system.get_user_profile(member.id)
            profile["_voice_join_time"] = datetime.now().timestamp()
            self.profile_system.update_user_profile(member.id, profile)
        
        # Si l'utilisateur quitte un vocal
        elif before.channel is not None and after.channel is None:
            profile = self.profile_system.get_user_profile(member.id)
            if "_voice_join_time" in profile:
                voice_time = datetime.now().timestamp() - profile["_voice_join_time"]
                await self.profile_system.update_user_statistics(member.id, "voice_time", int(voice_time))
                del profile["_voice_join_time"]
                self.profile_system.update_user_profile(member.id, profile)

async def setup(bot):
    """Setup du cog profils utilisateurs"""
    await bot.add_cog(UserProfileCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(profile_group)
    
    log.info("👤 Système de Profils Utilisateurs chargé avec succès")
