#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ ARSENAL V4 - SYSTÈME D'AUTOMOD ULTRA-AVANCÉ
Détection spam, filtres, auto-sanctions, configuration complète

🔄 HOT-RELOAD: Version 1.0 - Système rechargeable à chaud
⚡ Test du système: Modifiez ce commentaire et utilisez /reload module automod_system
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import time
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.logger import log
from manager.config_manager import config_data, save_config, load_config

class AutoModSystem:
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/automod_config.json"
        self.user_message_history = {}  # Historique des messages pour détection spam
        self.user_warnings = {}  # Système d'avertissements
        self.raid_tracker = {}  # Suivi des raids par serveur
        self.competing_bots = {}  # Bots concurrents détectés par serveur
        self.load_config()
        
    def load_config(self):
        """Charge la configuration automod"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                log.info("🛡️ Configuration automod chargée")
            except Exception as e:
                log.error(f"❌ Erreur chargement automod config: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            log.info("💾 Configuration automod sauvegardée")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde automod: {e}")
    
    async def detect_competing_bots(self, guild: discord.Guild):
        """Détecte les bots concurrents d'automod/modération"""
        competing_bots = []
        
        # Liste des bots d'automod/modération connus
        known_automod_bots = {
            "Carl-bot": [235148962103951360],
            "Dyno": [155149108183695360],
            "MEE6": [159985870458322944],
            "Ticket Tool": [557628352828014614],
            "Dank Memer": [270904126974590976],
            "YAGPDB": [204255221017214977],
            "Groovy": [234395307759108106],
            "Rythm": [235088799074484224],
            "Mudae": [432610292342587392],
            "Pancake": [239631525350604801],
            "GiveawayBot": [396464677032329216],
            "Pokecord": [365975655608745985],
            "Nadeko": [116275390695079945],
            "UnbelievaBoat": [292953664492929025],
            "ServerStats": [458276816071950337],
            "Statbot": [297045071457681409],
            "Discord Tickets": [514429412392984597]
        }
    
    async def detect_welcome_bots(self, guild: discord.Guild):
        """Détecte spécifiquement les bots de bienvenue pour éviter les doublons"""
        welcome_bots = []
        
        # Bots de bienvenue populaires
        welcome_bot_list = {
            "Carl-bot": [235148962103951360],
            "Dyno": [155149108183695360], 
            "MEE6": [159985870458322944],
            "YAGPDB": [204255221017214977],
            "UnbelievaBoat": [292953664492929025],
            "Pancake": [239631525350604801],
            "GiveawayBot": [396464677032329016],
            "Welcome Bot": [330416853971107840],
            "Welcomer": [330416853971107840],
            "Ticket Tool": [557628352828014614]
        }
        
        for member in guild.members:
            if member.bot:
                for bot_name, bot_ids in welcome_bot_list.items():
                    if member.id in bot_ids:
                        # Vérifier si le bot a des permissions pour envoyer des messages
                        permissions = member.guild_permissions
                        can_welcome = any([
                            permissions.send_messages,
                            permissions.manage_messages,
                            permissions.embed_links
                        ])
                        
                        if can_welcome:
                            welcome_bots.append({
                                "name": bot_name,
                                "mention": member.mention,
                                "id": member.id,
                                "disable_commands": self.get_welcome_disable_commands(bot_name)
                            })
        
        return welcome_bots
    
    def get_welcome_disable_commands(self, bot_name: str):
        """Retourne les commandes pour désactiver les messages de bienvenue"""
        commands_map = {
            "Carl-bot": [
                "/automod welcomer disable",
                "/welcomer disable"
            ],
            "Dyno": [
                "?modules disable Autoresponder",
                "Dashboard: dynobot.net > Modules > Autoresponder"
            ],
            "MEE6": [
                "Dashboard: mee6.xyz > Welcome > Disable",
                "/welcome disable"
            ],
            "YAGPDB": [
                "Dashboard: yagpdb.xyz > Autorole & Welcome messages > Disable"
            ],
            "UnbelievaBoat": [
                "/settings welcome disable"
            ],
            "Pancake": [
                "/config welcome disable"
            ],
            "Welcome Bot": [
                "/settings toggle welcome off"
            ],
            "Ticket Tool": [
                "/config welcome disable"
            ]
        }
        return commands_map.get(bot_name, ["Vérifiez les paramètres du bot"])
        
        # Vérifier chaque bot sur le serveur
        for member in guild.members:
            if member.bot:
                for bot_name, bot_ids in known_automod_bots.items():
                    if member.id in bot_ids:
                        # Vérifier les permissions du bot concurrent
                        permissions = member.guild_permissions
                        has_mod_perms = any([
                            permissions.manage_messages,
                            permissions.kick_members,
                            permissions.ban_members,
                            permissions.manage_roles,
                            permissions.moderate_members
                        ])
                        
                        if has_mod_perms:
                            competing_bots.append({
                                "name": bot_name,
                                "mention": member.mention,
                                "id": member.id,
                                "permissions": {
                                    "manage_messages": permissions.manage_messages,
                                    "kick_members": permissions.kick_members,
                                    "ban_members": permissions.ban_members,
                                    "manage_roles": permissions.manage_roles,
                                    "moderate_members": permissions.moderate_members
                                }
                            })
        
        return competing_bots

    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "enabled": True,
            "competing_bots_detected": [],  # Bots concurrents détectés
            "auto_disable_competitors": False,  # Désactivation auto (défaut: non)
            "spam_detection": {
                "enabled": True,
                "max_messages": 5,  # Messages max en X secondes
                "time_window": 5,   # Fenêtre de temps en secondes
                "max_duplicates": 3,  # Messages identiques max
                "action": "mute",   # warn, mute, kick, ban
                "duration": 300     # Durée mute en secondes
            },
            "word_filter": {
                "enabled": True,
                "use_advanced_filter": True,  # Nouveau système avancé par niveaux
                "level_1_action": "warn",      # Grossièretés légères
                "level_2_action": "timeout",   # Insultes offensantes  
                "level_2_duration": 300,       # 5 minutes
                "level_3_action": "timeout",   # Vulgarités sexuelles
                "level_3_duration": 1800,      # 30 minutes
                "level_4_action": "timeout",   # Haine raciale/Extrême
                "level_4_duration": 7200,      # 2 heures
                "auto_delete": True,
                "words": [
                    "fuck", "shit", "bitch", "ass", "damn", 
                    "putain", "merde", "connard", "salope", "con"
                ],
                "action": "warn",   # Action pour mots basiques (legacy)
                # Base de données avancée par niveaux
                "level_1_words": [
                    "abruti","abrutis","abrutie","abruties","abrut1","abrvt1",
                    "andouille","andouilles","and0uille","and0uil1e",
                    "banane","bananes","b4n4ne","b@nane",
                    "boulet","boulets","b0ulet","b0ulets",
                    "bête","betes","b3te","b3t3",
                    "blaireau","blaireaux","bl4ireau","bl@ireau",
                    "casse-pieds","casse pieds","c4sse pieds",
                    "cloche","cloches","cl0che","cl0ches",
                    "clown","clowns","cl0wn","cl0wns",
                    "cornichon","cornichons","c0rnichon","c0rn1chon",
                    "crétin","cretins","cr3tin","cr3t1n",
                    "cruche","cruches","crvche","crvches",
                    "debile","debiles","débile","débiles","d3bile","d3b1le",
                    "gogole","gogoles","g0g0le","g0g0l3",
                    "gourdasse","gourdasses","g0urdasse","g0vrdasse",
                    "gourde","gourdes","g0urde","g0vrd3",
                    "idiot","idiots","1diot","1diots",
                    "imbécile","imbéciles","imb3cile","imb3c1le",
                    "naze","nazes","n4ze","n4z3",
                    "nul","nuls","nu1","nu1s",
                    "pignouf","pignoufs","p1gn0uf","p1gn0uƒ",
                    "plouc","ploucs","pl0uc","pl0vcs",
                    "tocard","tocards","t0card","t0c4rd",
                    "triple buse","triple buses","tr1ple buse",
                    "trouduc","trou du cul","tr0uduc","tr0u du cul",
                    "zigoto","zigotos","z1goto","z1g0t0",
                    "zouave","zouaves","z0uave","z0uav3",
                    "moron","dummy","stupid","loser","fool","nitwit",
                    "numbskull","dope","twit","donkey","silly","jerk"
                ],
                "level_2_words": [
                    "abruti fini","andouille finie",
                    "baltringue","baltringues","b4ltr1ngue","b@ltr1ngue",
                    "batard","bâtard","batards","bâtards","b4tard","b4t4rd","b@tard","b@t4rd",
                    "bouffon","bouffons","b0uffon","b0uff0n",
                    "bouffonne","bouffonnes","b0uffonne","b0uff0nn3",
                    "connard","connards","c0nnard","c0nn4rd","konnard","konar",
                    "connasse","connasses","c0nnasse","c0nn@ss3","konnasse","konasse",
                    "crétin fini","crétine finie","cr3tin fini",
                    "culé","culés","cvlé","cv1é",
                    "débile profond","d3bile profond",
                    "enculé","enculés","encule","encules","encvlé","3nculé","3ncul3","nculé",
                    "enflure","enflures","3nflure","3nflvres",
                    "face de rat","face de con","tête de con","tête de noeud",
                    "fils de chien","fils de pute","f1ls de ch13n","f1ls de put3",
                    "grognasse","grognasses","gr0gnasse","gr0gn@ss3",
                    "guignol","guignols","gu1gnol","gu1gn0l",
                    "idiot de service","imbécile fini",
                    "mange-merde","mange m*rde","mange m3rde",
                    "merdeux","merdeuse","m3rdeux","m3rdeuse",
                    "pauv' con","pauvre con","pauvre conne",
                    "pédé","pd","pédés","pédale","pdale","p3dé","p3d3","p3dale",
                    "pleutre","pleutres","pl3utre",
                    "pourri","pourris","p0urri","p0urr1",
                    "raté","ratés","r4té","r4t3",
                    "sale con","sale conne","s4le con","s4le c0nne",
                    "tapette","tapettes","t4pette","t4p3tte",
                    "toxico","toxicos","t0xico","t0x1co",
                    "trou de balle","troudeballe","troudeb4lle",
                    "vaurien","vauriens","v@urien","v@vr1en",
                    "wanker","tosser","bollocks","git","twat","prick","arse","bastard"
                ],
                "level_3_words": [
                    "baiseur","baiseurs","b4iseur","b@iseur",
                    "baiseuse","baiseuses","b4iseuse","b@iseuse",
                    "baiser ta mère","baisé ta mère","b4iser ta m3re","b@isé ta m3r3",
                    "baisable","baisables","b4isable","b@isable",
                    "branleur","branleuse","branleurs","branleuses","br4nleur","br@nleur",
                    "branlette","branlettes","br4nlette","br@nlette",
                    "chaudasse","chaudasses","ch0udasse","ch@udass3",
                    "chienne","chiennes","ch1enne","ch1enn3",
                    "couilles","couille","couillons","c0uille","c0u1lle","c0u1ll0ns",
                    "cul","culs","cv1","cv1s","kvl","kul",
                    "fellation","foutre","f0utre","f0uttr3",
                    "gouine","gouines","g0uine","g0uin3",
                    "jouir","jouis","j0uir","j0u1r",
                    "merdier","merdiers","m3rdier","m3rd1ers",
                    "niquer","niqué","niqués","n!quer","n1quer","n!ké","n1ké",
                    "nique ta mère","nique ta race","n1que ta m3re","n1que ta r4ce",
                    "péter le cul","pète le cul","p3ter le cvl","p3te le cvl",
                    "pipe","pipes","p!pe","p1pe",
                    "pisse","pisses","p!sse","p1sse",
                    "pucelle","pucelles","pvcelle","pvcell3",
                    "putain","putains","put1","put1n","put@in","pvtain",
                    "pute","putes","pvt3","pvtte","put3","put€",
                    "queutard","queue","queues","qu3ue","qu3u3",
                    "salope","salopes","s4lope","s4l0p3",
                    "sodomie","sodomiser","s0domie","s0dom1ser",
                    "suce","sucer","suceur","suceuse","sucettemoi",
                    "trou du cul","trouduc","tr0u du cvl","tr0uduc",
                    "zob","zboub","zb0ub","zb0bb",
                    "cocksucker","motherfucker","slut","whore","cum","pussy","dick","asshole","faggot","dyke","bitch","cock","jerkoff"
                ],
                "level_4_words": [
                    "sale arabe","sale bougnoule","bougnoul","b0ugnoule","b0ugn0ul",
                    "sale noir","sale nègre","nègre","nègres","n3gre","n3gr3","n1gre",
                    "sale blanc","sale caucasien","sale gaulois",
                    "sale juif","youpin","youpine","y0upin","y0up1n",
                    "sale musulman","sale islamiste","sale catho","sale chrétien",
                    "sale pédé","sale tarlouze","sale fiotte",
                    "sale gouine","sale lesbienne",
                    "chinois de merde","chinetoque","chinetoques","chinetoqu3",
                    "raton","ratons","r4ton","r4t0n",
                    "nazi","nazis","n4zi","n4z1",
                    "hitler","hitl3r","h!tler",
                    "terroriste","terroristes","t3rroriste","t3rror1st3",
                    "sale porc","sale chienne d'arabe","sale chien de juif",
                    "enculé de ta race","enculé de ta mère la race",
                    "nique les blancs","nique les noirs","nique les arabes","nique les juifs",
                    "crève sale","crève ta race","crève arabe","crève bougnoule",
                    "sale bâtard de blanc","sale bâtard de noir","sale bâtard d'arabe",
                    "sale fils de pute raciste",
                    "dirty nigger","n1gger","n!gger","nigg3r",
                    "sand nigger","monkey","ape","chink","gook","spic","kike",
                    "fucking jew","fucking muslim","fucking black","fucking white",
                    "white trash","black trash","islamic pig","christian pig",
                    "gas the jews","burn the muslims","kill all blacks","kill all whites",
                    "exterminate jews","exterminate muslims","exterminate blacks",
                    "hang the niggers","lynch the blacks","burn the gays","burn the faggots",
                    "death to jews","death to muslims","death to christians"
                ]
            },
            "caps_filter": {
                "enabled": True,
                "max_caps_percentage": 70,  # % majuscules max
                "min_message_length": 10,   # Longueur min pour vérification
                "action": "warn"
            },
            "mention_spam": {
                "enabled": True,
                "max_mentions": 5,  # Mentions max par message
                "action": "mute",
                "duration": 600
            },
            "link_filter": {
                "enabled": False,
                "whitelist": ["discord.gg", "youtube.com", "github.com"],
                "action": "delete"
            },
            "raid_protection": {
                "enabled": True,
                "max_joins": 10,    # Nouveaux membres max en X secondes
                "time_window": 30,  # Fenêtre de temps
                "action": "lockdown"  # lockdown, kick_new_members
            },
            "auto_sanctions": {
                "enabled": True,
                "warn_threshold": 3,    # Warnings avant action
                "mute_duration": 600,   # 10 minutes
                "ban_duration": 86400   # 24h (0 = permanent)
            },
            "exempt_roles": [],  # Rôles exempts
            "exempt_channels": [],  # Salons exempts
            "log_channel": None,  # Salon de logs
            "servers": {}  # Config par serveur
        }
    
    def get_server_config(self, guild_id: int):
        """Récupère la config pour un serveur spécifique"""
        guild_id = str(guild_id)
        if guild_id not in self.config["servers"]:
            self.config["servers"][guild_id] = self.get_default_config()
            self.save_config()
        return self.config["servers"][guild_id]
    
    def update_server_config(self, guild_id: int, new_config: dict):
        """Met à jour la config d'un serveur"""
        guild_id = str(guild_id)
        self.config["servers"][guild_id] = new_config
        self.save_config()
    
    async def is_exempt(self, message: discord.Message) -> bool:
        """Vérifie si l'utilisateur/salon est exempt"""
        config = self.get_server_config(message.guild.id)
        
        # Vérification des rôles exempts
        if message.author.guild_permissions.administrator:
            return True
            
        user_role_ids = [role.id for role in message.author.roles]
        if any(role_id in config["exempt_roles"] for role_id in user_role_ids):
            return True
            
        # Vérification des salons exempts
        if message.channel.id in config["exempt_channels"]:
            return True
            
        return False
    
    async def log_action(self, guild: discord.Guild, action: str, user: discord.Member, reason: str, details: str = ""):
        """Log les actions d'automod"""
        config = self.get_server_config(guild.id)
        log_channel_id = config.get("log_channel")
        
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="🛡️ Action AutoMod",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="👤 Utilisateur", value=f"{user.mention} ({user.id})", inline=True)
                embed.add_field(name="⚡ Action", value=action, inline=True)
                embed.add_field(name="📝 Raison", value=reason, inline=True)
                if details:
                    embed.add_field(name="📋 Détails", value=details, inline=False)
                embed.set_footer(text=f"Arsenal AutoMod • {guild.name}")
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    log.error(f"❌ Erreur envoi log automod: {e}")
    
    async def apply_sanction(self, message: discord.Message, action: str, reason: str, duration: int = 0):
        """Applique une sanction"""
        user = message.author
        guild = message.guild
        
        try:
            if action == "warn":
                # Système d'avertissement
                user_id = str(user.id)
                guild_id = str(guild.id)
                
                if guild_id not in self.user_warnings:
                    self.user_warnings[guild_id] = {}
                if user_id not in self.user_warnings[guild_id]:
                    self.user_warnings[guild_id][user_id] = 0
                
                self.user_warnings[guild_id][user_id] += 1
                warnings = self.user_warnings[guild_id][user_id]
                
                await message.channel.send(f"⚠️ {user.mention}, avertissement ({warnings}/3) : {reason}")
                await self.log_action(guild, f"Avertissement ({warnings}/3)", user, reason)
                
                # Vérifier si seuil d'avertissements atteint
                config = self.get_server_config(guild.id)
                if warnings >= config["auto_sanctions"]["warn_threshold"]:
                    await self.apply_sanction(message, "mute", f"Seuil d'avertissements atteint ({warnings})", 
                                            config["auto_sanctions"]["mute_duration"])
            
            elif action == "delete":
                await message.delete()
                await self.log_action(guild, "Message supprimé", user, reason, f"Contenu: {message.content[:100]}...")
            
            elif action == "mute":
                # Mute temporaire
                timeout_until = datetime.utcnow() + timedelta(seconds=duration)
                await user.timeout(timeout_until, reason=f"AutoMod: {reason}")
                
                time_str = f"{duration//60}min {duration%60}s" if duration >= 60 else f"{duration}s"
                await message.channel.send(f"🔇 {user.mention} a été rendu muet pour {time_str}. Raison: {reason}")
                await self.log_action(guild, f"Mute ({time_str})", user, reason)
            
            elif action == "kick":
                await user.kick(reason=f"AutoMod: {reason}")
                await message.channel.send(f"👢 {user.mention} a été expulsé. Raison: {reason}")
                await self.log_action(guild, "Kick", user, reason)
            
            elif action == "ban":
                ban_duration = timedelta(seconds=duration) if duration > 0 else None
                await user.ban(reason=f"AutoMod: {reason}", delete_message_days=1)
                
                duration_str = f" ({duration//3600}h)" if duration > 0 else " (permanent)"
                await message.channel.send(f"🔨 {user.mention} a été banni{duration_str}. Raison: {reason}")
                await self.log_action(guild, f"Ban{duration_str}", user, reason)
        
        except Exception as e:
            log.error(f"❌ Erreur application sanction {action}: {e}")
    
    async def check_spam(self, message: discord.Message) -> bool:
        """Détecte le spam/flood"""
        config = self.get_server_config(message.guild.id)
        if not config["spam_detection"]["enabled"]:
            return False
        
        user_id = message.author.id
        current_time = time.time()
        
        # Initialiser l'historique utilisateur
        if user_id not in self.user_message_history:
            self.user_message_history[user_id] = []
        
        # Ajouter le message actuel
        self.user_message_history[user_id].append({
            "time": current_time,
            "content": message.content,
            "channel": message.channel.id
        })
        
        # Nettoyer les anciens messages
        time_window = config["spam_detection"]["time_window"]
        self.user_message_history[user_id] = [
            msg for msg in self.user_message_history[user_id]
            if current_time - msg["time"] <= time_window
        ]
        
        recent_messages = self.user_message_history[user_id]
        
        # Vérifier le nombre de messages
        if len(recent_messages) > config["spam_detection"]["max_messages"]:
            await self.apply_sanction(
                message, 
                config["spam_detection"]["action"],
                f"Spam détecté ({len(recent_messages)} messages en {time_window}s)",
                config["spam_detection"]["duration"]
            )
            return True
        
        # Vérifier les doublons
        content_count = {}
        for msg in recent_messages:
            content = msg["content"].lower().strip()
            content_count[content] = content_count.get(content, 0) + 1
        
        max_duplicates = config["spam_detection"]["max_duplicates"]
        for content, count in content_count.items():
            if count > max_duplicates and content:
                await self.apply_sanction(
                    message,
                    config["spam_detection"]["action"],
                    f"Messages identiques répétés ({count} fois)",
                    config["spam_detection"]["duration"]
                )
                return True
        
        return False
    
    async def check_word_filter(self, message: discord.Message) -> bool:
        """Filtre les mots interdits avec système avancé par niveaux"""
        config = self.get_server_config(message.guild.id)
        if not config["word_filter"]["enabled"]:
            return False
        
        content = message.content.lower()
        
        # Nouveau système avancé par niveaux
        if config["word_filter"].get("use_advanced_filter", True):
            return await self.check_advanced_word_filter(message, config, content)
        
        # Ancien système basique (fallback)
        forbidden_words = config["word_filter"]["words"]
        
        for word in forbidden_words:
            if word.lower() in content:
                if config["word_filter"]["auto_delete"]:
                    await self.apply_sanction(message, "delete", f"Mot interdit détecté: {word}")
                
                await self.apply_sanction(
                    message,
                    config["word_filter"]["action"],
                    f"Utilisation de mot interdit: {word}"
                )
                return True
        
        return False
    
    async def check_advanced_word_filter(self, message: discord.Message, config: dict, content: str) -> bool:
        """Système de filtrage avancé par niveaux de gravité"""
        
        # Niveau 4 - Haine raciale/Extrême (priorité maximale)
        level_4_words = config["word_filter"].get("level_4_words", [])
        for word in level_4_words:
            if word.lower() in content:
                if config["word_filter"]["auto_delete"]:
                    await self.apply_sanction(message, "delete", f"Contenu haineux détecté")
                
                # Timeout 2 heures + log spécial
                duration = config["word_filter"].get("level_4_duration", 7200)
                await self.apply_sanction(
                    message,
                    config["word_filter"]["level_4_action"],
                    f"🚨 Contenu haineux/raciste détecté (Niveau 4)",
                    duration
                )
                
                # Log spécial pour le niveau 4
                await self.log_hate_speech(message, word, "Niveau 4 - Haine raciale/Extrême")
                return True
        
        # Niveau 3 - Vulgarités sexuelles
        level_3_words = config["word_filter"].get("level_3_words", [])
        for word in level_3_words:
            if word.lower() in content:
                if config["word_filter"]["auto_delete"]:
                    await self.apply_sanction(message, "delete", f"Contenu sexuel détecté")
                
                duration = config["word_filter"].get("level_3_duration", 1800)  # 30 min
                await self.apply_sanction(
                    message,
                    config["word_filter"]["level_3_action"],
                    f"⚠️ Vulgarité sexuelle détectée (Niveau 3)",
                    duration
                )
                return True
        
        # Niveau 2 - Insultes offensantes
        level_2_words = config["word_filter"].get("level_2_words", [])
        for word in level_2_words:
            if word.lower() in content:
                if config["word_filter"]["auto_delete"]:
                    await self.apply_sanction(message, "delete", f"Insulte détectée")
                
                duration = config["word_filter"].get("level_2_duration", 300)  # 5 min
                await self.apply_sanction(
                    message,
                    config["word_filter"]["level_2_action"],
                    f"💢 Insulte offensante détectée (Niveau 2)",
                    duration
                )
                return True
        
        # Niveau 1 - Grossièretés légères
        level_1_words = config["word_filter"].get("level_1_words", [])
        for word in level_1_words:
            if word.lower() in content:
                if config["word_filter"]["auto_delete"]:
                    await self.apply_sanction(message, "delete", f"Grossièreté détectée")
                
                await self.apply_sanction(
                    message,
                    config["word_filter"]["level_1_action"],
                    f"😠 Grossièreté détectée (Niveau 1)"
                )
                return True
        
        return False
    
    async def log_hate_speech(self, message: discord.Message, word: str, level: str):
        """Log spécial pour les contenus haineux (Niveau 4)"""
        config = self.get_server_config(message.guild.id)
        log_channel_id = config.get("log_channel")
        
        if log_channel_id:
            log_channel = message.guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="🚨 ALERTE - Contenu Haineux Détecté",
                    description=f"**{level}**",
                    color=discord.Color.dark_red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="👤 Utilisateur", value=f"{message.author.mention} ({message.author.id})", inline=True)
                embed.add_field(name="📍 Salon", value=f"{message.channel.mention}", inline=True)
                embed.add_field(name="⚡ Action", value="Timeout 2h + Suppression", inline=True)
                embed.add_field(name="🔍 Mot détecté", value=f"||{word}||", inline=False)
                embed.add_field(name="📝 Message", value=f"||{message.content[:200]}...||", inline=False)
                embed.add_field(name="⚠️ Attention", value="Ce type de contenu peut nécessiter une action manuelle supplémentaire", inline=False)
                embed.set_footer(text=f"Arsenal AutoMod • Surveillance Niveau 4")
                
                try:
                    await log_channel.send(embed=embed)
                    # Ping les modérateurs pour les cas graves
                    await log_channel.send("🚨 @here - Contenu haineux détecté, vérification manuelle recommandée")
                except Exception as e:
                    log.error(f"❌ Erreur envoi log hate speech: {e}")
        
        # Log également dans les logs système
        log.warning(f"🚨 HATE SPEECH détecté sur {message.guild.name} par {message.author} ({message.author.id}): {word}")
    
    async def apply_sanction(self, message: discord.Message, action: str, reason: str, duration: int = 0):
        """Applique une sanction avec support des timeouts avancés"""
        user = message.author
        guild = message.guild
        
        try:
            if action == "warn":
                # Système d'avertissement
                user_id = str(user.id)
                guild_id = str(guild.id)
                
                if guild_id not in self.user_warnings:
                    self.user_warnings[guild_id] = {}
                if user_id not in self.user_warnings[guild_id]:
                    self.user_warnings[guild_id][user_id] = 0
                
                self.user_warnings[guild_id][user_id] += 1
                warnings = self.user_warnings[guild_id][user_id]
                
                await message.channel.send(f"⚠️ {user.mention}, avertissement ({warnings}/3) : {reason}")
                await self.log_action(guild, f"Avertissement ({warnings}/3)", user, reason)
                
                # Vérifier si seuil d'avertissements atteint
                config = self.get_server_config(guild.id)
                if warnings >= config["auto_sanctions"]["warn_threshold"]:
                    await self.apply_sanction(message, "timeout", f"Seuil d'avertissements atteint ({warnings})", 
                                            config["auto_sanctions"]["mute_duration"])
            
            elif action == "delete":
                await message.delete()
                await self.log_action(guild, "Message supprimé", user, reason, f"Contenu: {message.content[:100]}...")
            
            elif action in ["mute", "timeout"]:
                # Timeout temporaire (nouvelle API Discord)
                timeout_until = datetime.utcnow() + timedelta(seconds=duration)
                await user.timeout(timeout_until, reason=f"AutoMod: {reason}")
                
                # Formatage intelligent de la durée
                if duration >= 3600:  # Plus d'1 heure
                    time_str = f"{duration//3600}h{(duration%3600)//60:02d}min"
                elif duration >= 60:  # Plus d'1 minute
                    time_str = f"{duration//60}min{duration%60:02d}s"
                else:
                    time_str = f"{duration}s"
                
                # Message adapté selon la gravité
                if duration >= 3600:  # Sanctions lourdes
                    await message.channel.send(f"🔇 {user.mention} a été mis en timeout pour **{time_str}**.\n📋 Raison: {reason}")
                else:  # Sanctions légères
                    await message.channel.send(f"🔇 {user.mention} timeout {time_str} - {reason}")
                
                await self.log_action(guild, f"Timeout ({time_str})", user, reason)
            
            elif action == "kick":
                await user.kick(reason=f"AutoMod: {reason}")
                await message.channel.send(f"👢 {user.mention} a été expulsé. Raison: {reason}")
                await self.log_action(guild, "Kick", user, reason)
            
            elif action == "ban":
                ban_duration = timedelta(seconds=duration) if duration > 0 else None
                await user.ban(reason=f"AutoMod: {reason}", delete_message_days=1)
                
                duration_str = f" ({duration//3600}h)" if duration > 0 else " (permanent)"
                await message.channel.send(f"🔨 {user.mention} a été banni{duration_str}. Raison: {reason}")
                await self.log_action(guild, f"Ban{duration_str}", user, reason)
        
        except Exception as e:
            log.error(f"❌ Erreur application sanction {action}: {e}")
            # En cas d'erreur, essayer une sanction de fallback
            if action == "timeout" and duration > 0:
                try:
                    # Fallback vers un mute de rôle si timeout échoue
                    await message.channel.send(f"⚠️ Erreur timeout pour {user.mention}, veuillez appliquer une sanction manuelle")
                except:
                    pass
    
    async def check_caps_filter(self, message: discord.Message) -> bool:
        """Filtre les messages en majuscules excessives"""
        config = self.get_server_config(message.guild.id)
        if not config["caps_filter"]["enabled"]:
            return False
        
        content = message.content
        if len(content) < config["caps_filter"]["min_message_length"]:
            return False
        
        caps_count = sum(1 for c in content if c.isupper())
        caps_percentage = (caps_count / len(content)) * 100
        
        if caps_percentage > config["caps_filter"]["max_caps_percentage"]:
            await self.apply_sanction(
                message,
                config["caps_filter"]["action"],
                f"Trop de majuscules ({caps_percentage:.1f}%)"
            )
            return True
        
        return False
    
    async def check_mention_spam(self, message: discord.Message) -> bool:
        """Détecte le spam de mentions"""
        config = self.get_server_config(message.guild.id)
        if not config["mention_spam"]["enabled"]:
            return False
        
        mention_count = len(message.mentions) + len(message.role_mentions)
        
        if mention_count > config["mention_spam"]["max_mentions"]:
            await self.apply_sanction(
                message,
                config["mention_spam"]["action"],
                f"Spam de mentions ({mention_count} mentions)",
                config["mention_spam"]["duration"]
            )
            return True
        
        return False
    
    async def check_link_filter(self, message: discord.Message) -> bool:
        """Filtre les liens non autorisés"""
        config = self.get_server_config(message.guild.id)
        if not config["link_filter"]["enabled"]:
            return False
        
        # Regex pour détecter les URLs
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        urls = url_pattern.findall(message.content)
        whitelist = config["link_filter"]["whitelist"]
        
        for url in urls:
            allowed = any(domain in url for domain in whitelist)
            if not allowed:
                await self.apply_sanction(
                    message,
                    config["link_filter"]["action"],
                    f"Lien non autorisé: {url[:50]}..."
                )
                return True
        
        return False
    
    async def process_message(self, message: discord.Message):
        """Traite un message avec tous les filtres"""
        if message.author.bot or not message.guild:
            return
        
        config = self.get_server_config(message.guild.id)
        if not config["enabled"]:
            return
        
        if await self.is_exempt(message):
            return
        
        # Appliquer tous les filtres
        await self.check_spam(message)
        await self.check_word_filter(message)
        await self.check_caps_filter(message)
        await self.check_mention_spam(message)
        await self.check_link_filter(message)

# Commandes slash pour l'automod
automod_group = app_commands.Group(name="automod", description="🛡️ Configuration du système d'auto-modération")

@automod_group.command(name="status", description="Affiche le statut de l'automod")
async def automod_status(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    status = "🟢 Activé" if config["enabled"] else "🔴 Désactivé"
    
    embed = discord.Embed(
        title="🛡️ Statut AutoMod Arsenal",
        description=f"**Statut global:** {status}",
        color=discord.Color.green() if config["enabled"] else discord.Color.red()
    )
    
    # Modules
    modules_status = []
    modules = [
        ("spam_detection", "🚫 Anti-Spam"),
        ("word_filter", "🤬 Filtre de mots"),
        ("caps_filter", "🔠 Filtre majuscules"),
        ("mention_spam", "📢 Anti-mention spam"),
        ("link_filter", "🔗 Filtre de liens"),
        ("raid_protection", "🛡️ Protection raid")
    ]
    
    for module_key, module_name in modules:
        status_icon = "🟢" if config[module_key]["enabled"] else "🔴"
        modules_status.append(f"{status_icon} {module_name}")
    
    embed.add_field(
        name="📋 Modules",
        value="\n".join(modules_status),
        inline=True
    )
    
    # Statistiques
    guild_warnings = automod.user_warnings.get(str(interaction.guild.id), {})
    total_warnings = sum(guild_warnings.values())
    
    embed.add_field(
        name="📊 Statistiques",
        value=f"**Avertissements:** {total_warnings}\n**Utilisateurs suivis:** {len(guild_warnings)}",
        inline=True
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@automod_group.command(name="toggle", description="Active/désactive l'automod")
@app_commands.checks.has_permissions(administrator=True)
async def automod_toggle(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    config["enabled"] = not config["enabled"]
    automod.update_server_config(interaction.guild.id, config)
    
    status = "activé" if config["enabled"] else "désactivé"
    emoji = "🟢" if config["enabled"] else "🔴"
    
    await interaction.response.send_message(f"{emoji} AutoMod {status} sur ce serveur", ephemeral=True)

@automod_group.command(name="config", description="Configure les paramètres d'automod")
@app_commands.describe(
    module="Module à configurer",
    setting="Paramètre à modifier",
    value="Nouvelle valeur"
)
@app_commands.choices(module=[
    app_commands.Choice(name="Anti-Spam", value="spam_detection"),
    app_commands.Choice(name="Filtre de mots", value="word_filter"),
    app_commands.Choice(name="Filtre majuscules", value="caps_filter"),
    app_commands.Choice(name="Anti-mention spam", value="mention_spam"),
    app_commands.Choice(name="Filtre liens", value="link_filter")
])
@app_commands.checks.has_permissions(administrator=True)
async def automod_config(interaction: discord.Interaction, module: str, setting: str, value: str):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    if module not in config:
        await interaction.response.send_message(f"❌ Module '{module}' introuvable", ephemeral=True)
        return
    
    try:
        # Conversion de la valeur selon le type
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        config[module][setting] = value
        automod.update_server_config(interaction.guild.id, config)
        
        await interaction.response.send_message(
            f"✅ {module}.{setting} = {value}", 
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

@automod_group.command(name="add_word", description="Ajoute un mot au filtre")
@app_commands.describe(word="Mot à ajouter au filtre")
@app_commands.checks.has_permissions(administrator=True)
async def add_word(interaction: discord.Interaction, word: str):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    if word.lower() not in [w.lower() for w in config["word_filter"]["words"]]:
        config["word_filter"]["words"].append(word.lower())
        automod.update_server_config(interaction.guild.id, config)
        await interaction.response.send_message(f"✅ Mot '{word}' ajouté au filtre", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Mot '{word}' déjà dans le filtre", ephemeral=True)

@automod_group.command(name="remove_word", description="Retire un mot du filtre")
@app_commands.describe(word="Mot à retirer du filtre")
@app_commands.checks.has_permissions(administrator=True)
async def remove_word(interaction: discord.Interaction, word: str):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    words_lower = [w.lower() for w in config["word_filter"]["words"]]
    if word.lower() in words_lower:
        # Trouver et supprimer le mot (en gardant la casse originale)
        for i, w in enumerate(config["word_filter"]["words"]):
            if w.lower() == word.lower():
                del config["word_filter"]["words"][i]
                break
        
        automod.update_server_config(interaction.guild.id, config)
        await interaction.response.send_message(f"✅ Mot '{word}' retiré du filtre", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Mot '{word}' non trouvé dans le filtre", ephemeral=True)

@automod_group.command(name="set_log_channel", description="Définit le salon de logs automod")
@app_commands.describe(channel="Salon pour les logs d'automod")
@app_commands.checks.has_permissions(administrator=True)
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    config["log_channel"] = channel.id
    automod.update_server_config(interaction.guild.id, config)
    
    await interaction.response.send_message(f"✅ Salon de logs défini: {channel.mention}", ephemeral=True)

@automod_group.command(name="warnings", description="Affiche les avertissements d'un utilisateur")
@app_commands.describe(user="Utilisateur à vérifier")
async def warnings(interaction: discord.Interaction, user: discord.Member):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    guild_warnings = automod.user_warnings.get(str(interaction.guild.id), {})
    user_warnings = guild_warnings.get(str(user.id), 0)
    
    embed = discord.Embed(
        title=f"⚠️ Avertissements - {user.display_name}",
        description=f"**Avertissements:** {user_warnings}/3",
        color=discord.Color.orange() if user_warnings > 0 else discord.Color.green()
    )
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@automod_group.command(name="clear_warnings", description="Efface les avertissements d'un utilisateur")
@app_commands.describe(user="Utilisateur à réinitialiser")
@app_commands.checks.has_permissions(administrator=True)
async def clear_warnings(interaction: discord.Interaction, user: discord.Member):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    user_id = str(user.id)
    
    if guild_id in automod.user_warnings and user_id in automod.user_warnings[guild_id]:
        del automod.user_warnings[guild_id][user_id]
        await interaction.response.send_message(f"✅ Avertissements effacés pour {user.mention}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Aucun avertissement trouvé pour {user.mention}", ephemeral=True)

@automod_group.command(name="detect_competitors", description="Détecte les bots d'automod concurrents sur le serveur")
@app_commands.checks.has_permissions(administrator=True)
async def detect_competitors(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Détecter les bots concurrents
    competing_bots = await automod.detect_competing_bots(interaction.guild)
    
    if not competing_bots:
        embed = discord.Embed(
            title="🔍 Détection Bots Concurrents",
            description="✅ Aucun bot d'automod concurrent détecté sur ce serveur.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Afficher les bots détectés
    embed = discord.Embed(
        title="⚠️ Bots d'AutoMod Concurrents Détectés",
        description=f"**{len(competing_bots)} bot(s) concurrent(s) trouvé(s) :**",
        color=discord.Color.orange()
    )
    
    for i, bot in enumerate(competing_bots, 1):
        perms_list = []
        for perm, has_perm in bot["permissions"].items():
            if has_perm:
                perm_emoji = {
                    "manage_messages": "🗑️",
                    "kick_members": "👢", 
                    "ban_members": "🔨",
                    "manage_roles": "🎭",
                    "moderate_members": "🔇"
                }
                perms_list.append(f"{perm_emoji.get(perm, '⚙️')} {perm.replace('_', ' ').title()}")
        
        embed.add_field(
            name=f"{i}. {bot['name']}",
            value=f"**Bot:** {bot['mention']}\n**Permissions:** {', '.join(perms_list) if perms_list else 'Aucune'}",
            inline=False
        )
    
    embed.add_field(
        name="💡 Que faire ?",
        value="• Vous pouvez désactiver manuellement les fonctions automod de ces bots\n• Ou utiliser `/automod takeover` pour proposer une désactivation assistée",
        inline=False
    )
    
    embed.set_footer(text="Arsenal AutoMod • Détection Concurrents")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@automod_group.command(name="check_welcome", description="Vérifie les bots de bienvenue concurrents avant configuration")
@app_commands.checks.has_permissions(administrator=True)
async def check_welcome_bots(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Détecter les bots de bienvenue
    welcome_bots = await automod.detect_welcome_bots(interaction.guild)
    
    if not welcome_bots:
        embed = discord.Embed(
            title="✅ Configuration Bienvenue",
            description="Aucun bot de bienvenue concurrent détecté.\nVous pouvez configurer Arsenal sans risque de doublons !",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Afficher les bots de bienvenue détectés
    embed = discord.Embed(
        title="⚠️ Bots de Bienvenue Détectés",
        description=f"**{len(welcome_bots)} bot(s) de bienvenue trouvé(s)** qui pourraient créer des doublons :",
        color=discord.Color.orange()
    )
    
    for i, bot in enumerate(welcome_bots, 1):
        commands_to_disable = "\n".join([f"• `{cmd}`" for cmd in bot["disable_commands"][:3]])
        
        embed.add_field(
            name=f"{i}. {bot['name']}",
            value=f"**Bot:** {bot['mention']}\n**Désactiver avec:**\n{commands_to_disable}",
            inline=False
        )
    
    embed.add_field(
        name="🔧 Actions Recommandées",
        value="1️⃣ Désactivez les messages de bienvenue des bots listés\n2️⃣ Configurez ensuite Arsenal avec `/admin setup_welcome`\n3️⃣ Utilisez `/automod disable_welcome_bots` pour une aide détaillée",
        inline=False
    )
    
    embed.set_footer(text="Arsenal AutoMod • Détection Bienvenue")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@automod_group.command(name="disable_welcome_bots", description="Guide pour désactiver les bots de bienvenue concurrents")
@app_commands.checks.has_permissions(administrator=True)  
async def disable_welcome_guide(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    welcome_bots = await automod.detect_welcome_bots(interaction.guild)
    
    if not welcome_bots:
        await interaction.followup.send("✅ Aucun bot de bienvenue concurrent détecté.", ephemeral=True)
        return
    
    # Guide détaillé de désactivation
    embed = discord.Embed(
        title="🛠️ Guide de Désactivation - Messages de Bienvenue",
        description="**Instructions détaillées pour éviter les doublons :**",
        color=discord.Color.blue()
    )
    
    for bot in welcome_bots:
        bot_name = bot["name"]
        commands = bot["disable_commands"]
        
        commands_text = "\n".join([f"• `{cmd}`" for cmd in commands])
        
        embed.add_field(
            name=f"🤖 {bot_name}",
            value=f"**Commandes:**\n{commands_text}",
            inline=False
        )
    
    embed.add_field(
        name="⚡ Après Désactivation",
        value="1️⃣ Utilisez `/admin setup_welcome` pour configurer Arsenal\n2️⃣ Testez avec `/admin test_welcome` pour vérifier\n3️⃣ Arsenal gérera tous les messages de bienvenue sans doublons",
        inline=False
    )
    
    embed.add_field(
        name="💡 Conseil Pro",
        value="Gardez les autres fonctionnalités de ces bots (musique, jeux, etc.)\nDésactivez SEULEMENT les messages de bienvenue !",
        inline=False
    )
    
    embed.set_footer(text="Arsenal AutoMod • Migration Bienvenue")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@automod_group.command(name="filter_status", description="Statut détaillé du système de filtrage par niveaux")
@app_commands.checks.has_permissions(administrator=True)
async def filter_status(interaction: discord.Interaction):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    embed = discord.Embed(
        title="🛡️ Statut Filtrage Avancé - Arsenal V4",
        description="**Système de filtrage par niveaux de gravité**",
        color=discord.Color.blue()
    )
    
    # Status général
    is_enabled = config["word_filter"]["enabled"]
    advanced_enabled = config["word_filter"].get("use_advanced_filter", True)
    
    embed.add_field(
        name="📊 État Général",
        value=f"**Filtrage:** {'🟢 Activé' if is_enabled else '🔴 Désactivé'}\n**Système avancé:** {'🟢 Activé' if advanced_enabled else '🔴 Désactivé'}",
        inline=True
    )
    
    if advanced_enabled and is_enabled:
        # Niveaux de sanctions
        level_info = [
            ("1️⃣ Grossièretés légères", config["word_filter"].get("level_1_action", "warn"), "Avertissement", len(config["word_filter"].get("level_1_words", []))),
            ("2️⃣ Insultes offensantes", config["word_filter"].get("level_2_action", "timeout"), f"{config['word_filter'].get('level_2_duration', 300)//60}min", len(config["word_filter"].get("level_2_words", []))),
            ("3️⃣ Vulgarités sexuelles", config["word_filter"].get("level_3_action", "timeout"), f"{config['word_filter'].get('level_3_duration', 1800)//60}min", len(config["word_filter"].get("level_3_words", []))),
            ("4️⃣ Haine raciale/Extrême", config["word_filter"].get("level_4_action", "timeout"), f"{config['word_filter'].get('level_4_duration', 7200)//3600}h", len(config["word_filter"].get("level_4_words", [])))
        ]
        
        levels_text = "\n".join([f"{level} → **{sanction}** ({duree}) • {count} mots" for level, action, duree, count in level_info])
        
        embed.add_field(
            name="⚖️ Sanctions par Niveau",
            value=levels_text,
            inline=False
        )
        
        # Statistiques
        total_words = sum([info[3] for info in level_info])
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Total mots surveillés:** {total_words}\n**Suppression auto:** {'🟢 Oui' if config['word_filter']['auto_delete'] else '🔴 Non'}",
            inline=True
        )
    
    embed.set_footer(text="Arsenal V4 • Filtrage Intelligent")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@automod_group.command(name="configure_levels", description="Configurer les sanctions par niveau")
@app_commands.describe(
    level="Niveau à configurer (1-4)",
    action="Type de sanction",
    duration="Durée en secondes (pour timeout uniquement)"
)
@app_commands.choices(
    level=[
        app_commands.Choice(name="Niveau 1 - Grossièretés légères", value=1),
        app_commands.Choice(name="Niveau 2 - Insultes offensantes", value=2),
        app_commands.Choice(name="Niveau 3 - Vulgarités sexuelles", value=3),
        app_commands.Choice(name="Niveau 4 - Haine raciale/Extrême", value=4)
    ],
    action=[
        app_commands.Choice(name="Avertissement", value="warn"),
        app_commands.Choice(name="Timeout", value="timeout"),
        app_commands.Choice(name="Kick", value="kick"),
        app_commands.Choice(name="Ban", value="ban")
    ]
)
@app_commands.checks.has_permissions(administrator=True)
async def configure_levels(interaction: discord.Interaction, level: int, action: str, duration: int = None):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    # Validation
    if level not in [1, 2, 3, 4]:
        await interaction.response.send_message("❌ Niveau invalide (1-4)", ephemeral=True)
        return
    
    # Configuration
    config["word_filter"][f"level_{level}_action"] = action
    
    if action == "timeout" and duration:
        config["word_filter"][f"level_{level}_duration"] = duration
    
    automod.update_server_config(interaction.guild.id, config)
    
    # Message de confirmation
    level_names = {1: "Grossièretés légères", 2: "Insultes offensantes", 3: "Vulgarités sexuelles", 4: "Haine raciale/Extrême"}
    
    response = f"✅ **Niveau {level}** ({level_names[level]}) configuré:\n"
    response += f"**Action:** {action}"
    if action == "timeout" and duration:
        if duration >= 3600:
            response += f"\n**Durée:** {duration//3600}h{(duration%3600)//60:02d}min"
        elif duration >= 60:
            response += f"\n**Durée:** {duration//60}min{duration%60:02d}s"
        else:
            response += f"\n**Durée:** {duration}s"
    
    await interaction.response.send_message(response, ephemeral=True)

@automod_group.command(name="test_filter", description="Tester le système de filtrage (sans appliquer de sanction)")
@app_commands.describe(text="Texte à tester")
@app_commands.checks.has_permissions(administrator=True)
async def test_filter(interaction: discord.Interaction, text: str):
    automod = interaction.client.get_cog('AutoModSystem')
    if not automod:
        await interaction.response.send_message("❌ Système automod non chargé", ephemeral=True)
        return
    
    config = automod.get_server_config(interaction.guild.id)
    
    if not config["word_filter"]["enabled"]:
        await interaction.response.send_message("❌ Le filtrage est désactivé sur ce serveur", ephemeral=True)
        return
    
    content = text.lower()
    detected_words = []
    
    # Test des niveaux
    levels = [
        (4, "level_4_words", "🚨 Haine raciale/Extrême"),
        (3, "level_3_words", "⚠️ Vulgarités sexuelles"),  
        (2, "level_2_words", "💢 Insultes offensantes"),
        (1, "level_1_words", "😠 Grossièretés légères")
    ]
    
    for level_num, words_key, level_name in levels:
        words_list = config["word_filter"].get(words_key, [])
        for word in words_list:
            if word.lower() in content:
                action = config["word_filter"].get(f"level_{level_num}_action", "warn")
                duration = config["word_filter"].get(f"level_{level_num}_duration", 0)
                
                if duration > 0:
                    if duration >= 3600:
                        duration_str = f"{duration//3600}h{(duration%3600)//60:02d}min"
                    elif duration >= 60:
                        duration_str = f"{duration//60}min{duration%60:02d}s"
                    else:
                        duration_str = f"{duration}s"
                    sanction_str = f"{action} ({duration_str})"
                else:
                    sanction_str = action
                
                detected_words.append(f"{level_name}: `{word}` → {sanction_str}")
                break  # Une seule détection par niveau pour éviter le spam
    
    if detected_words:
        embed = discord.Embed(
            title="🔍 Test Filtrage - Détections",
            description=f"**Texte testé:** ||{text}||\n\n**Mots détectés:**",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📝 Résultats",
            value="\n".join(detected_words),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Action",
            value="En situation réelle, la sanction du niveau le plus élevé serait appliquée",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="🔍 Test Filtrage - Aucune Détection",
            description=f"**Texte testé:** {text}\n\n✅ Aucun mot interdit détecté",
            color=discord.Color.green()
        )
    
    embed.set_footer(text="Arsenal V4 • Test Filtrage")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


class AutoModCog(commands.Cog):
    """Cog pour le système d'automod"""
    
    def __init__(self, bot):
        self.bot = bot
        self.automod = AutoModSystem(bot)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Traite tous les messages avec l'automod"""
        await self.automod.process_message(message)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Détection de raid lors des arrivées"""
        config = self.automod.get_server_config(member.guild.id)
        if not config["raid_protection"]["enabled"]:
            return
        
        # Initialiser le compteur de raid
        current_time = time.time()
        guild_id = str(member.guild.id)
        
        if not hasattr(self.automod, 'raid_tracker'):
            self.automod.raid_tracker = {}
        
        if guild_id not in self.automod.raid_tracker:
            self.automod.raid_tracker[guild_id] = []
        
        # Ajouter la nouvelle arrivée
        self.automod.raid_tracker[guild_id].append(current_time)
        
        # Nettoyer les anciennes entrées
        time_window = config["raid_protection"]["time_window"]
        self.automod.raid_tracker[guild_id] = [
            join_time for join_time in self.automod.raid_tracker[guild_id]
            if current_time - join_time <= time_window
        ]
        
        # Vérifier si seuil de raid atteint
        recent_joins = len(self.automod.raid_tracker[guild_id])
        max_joins = config["raid_protection"]["max_joins"]
        
        if recent_joins > max_joins:
            log.warning(f"🚨 Raid détecté sur {member.guild.name}: {recent_joins} arrivées en {time_window}s")
            
            # Appliquer l'action anti-raid
            action = config["raid_protection"]["action"]
            
            if action == "lockdown":
                # Verrouiller le serveur (désactiver les invitations)
                try:
                    for invite in await member.guild.invites():
                        await invite.delete(reason="Protection anti-raid Arsenal")
                    log.info(f"🔒 Serveur {member.guild.name} verrouillé (raid détecté)")
                except Exception as e:
                    log.error(f"❌ Erreur verrouillage serveur: {e}")
            
            elif action == "kick_new_members":
                # Kick les nouveaux membres récents
                try:
                    await member.kick(reason="Protection anti-raid Arsenal - Arrivée suspecte")
                    log.info(f"👢 {member} expulsé (protection anti-raid)")
                except Exception as e:
                    log.error(f"❌ Erreur kick anti-raid: {e}")
            
            # Log l'action
            await self.automod.log_action(
                member.guild,
                f"Protection anti-raid ({action})",
                member,
                f"Raid détecté: {recent_joins} arrivées en {time_window}s"
            )

async def setup(bot):
    """Setup du cog automod"""
    await bot.add_cog(AutoModCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(automod_group)
    
    log.info("🛡️ Système AutoMod chargé avec succès")
