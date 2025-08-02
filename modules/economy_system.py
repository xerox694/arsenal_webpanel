#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 ARSENAL V4 - SYSTÈME D'ÉCONOMIE & NIVELLEMENT
Argent, expérience, niveaux, boutique, banque, récompenses
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import random
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from core.logger import log

class EconomySystem:
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/economy_config.json"
        self.users_data_path = "data/users_economy.json"
        self.daily_cooldowns = {}  # Cooldowns pour daily
        self.work_cooldowns = {}   # Cooldowns pour work
        self.crime_cooldowns = {}  # Cooldowns pour crime
        self.load_config()
        self.load_users_data()
        
    def load_config(self):
        """Charge la configuration économie"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                log.info("💰 Configuration économie chargée")
            except Exception as e:
                log.error(f"❌ Erreur chargement économie config: {e}")
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
            log.info("💾 Configuration économie sauvegardée")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde économie: {e}")
    
    def load_users_data(self):
        """Charge les données utilisateurs"""
        if os.path.exists(self.users_data_path):
            try:
                with open(self.users_data_path, "r", encoding="utf-8") as f:
                    self.users_data = json.load(f)
                log.info("👥 Données utilisateurs économie chargées")
            except Exception as e:
                log.error(f"❌ Erreur chargement données utilisateurs: {e}")
                self.users_data = {}
        else:
            self.users_data = {}
            self.save_users_data()
    
    def save_users_data(self):
        """Sauvegarde les données utilisateurs"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.users_data_path, "w", encoding="utf-8") as f:
                json.dump(self.users_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde données utilisateurs: {e}")
    
    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "currency_name": "Arsenal Coins",
            "currency_symbol": "🪙",
            "starting_balance": 1000,
            "starting_xp": 0,
            "xp_per_message": {"min": 15, "max": 25},
            "xp_cooldown": 60,  # Secondes entre gains XP
            "level_multiplier": 100,  # XP nécessaire = niveau * multiplier
            "daily_reward": {"min": 500, "max": 1500},
            "work_reward": {"min": 200, "max": 800},
            "crime_reward": {"min": 100, "max": 2000},
            "crime_fail_penalty": {"min": 50, "max": 500},
            "crime_success_rate": 0.6,  # 60% de réussite
            "bank_interest_rate": 0.02,  # 2% par jour
            "shop_items": {
                "premium_role": {
                    "name": "🌟 Rôle Premium",
                    "description": "Rôle premium avec avantages exclusifs",
                    "price": 50000,
                    "type": "role",
                    "role_id": None,
                    "duration": 2592000  # 30 jours
                },
                "custom_color": {
                    "name": "🎨 Couleur Personnalisée",
                    "description": "Créer son propre rôle coloré",
                    "price": 25000,
                    "type": "custom_role",
                    "duration": 1209600  # 14 jours
                },
                "vip_channel": {
                    "name": "💎 Accès VIP",
                    "description": "Accès aux salons VIP privés",
                    "price": 75000,
                    "type": "channel_access",
                    "channel_ids": [],
                    "duration": 2592000  # 30 jours
                },
                "boost_xp": {
                    "name": "⚡ Boost XP x2",
                    "description": "Double l'expérience gagnée",
                    "price": 15000,
                    "type": "boost",
                    "multiplier": 2.0,
                    "duration": 604800  # 7 jours
                },
                "boost_money": {
                    "name": "💰 Boost Argent x1.5",
                    "description": "Augmente les gains d'argent de 50%",
                    "price": 20000,
                    "type": "boost",
                    "multiplier": 1.5,
                    "duration": 604800  # 7 jours
                }
            },
            "level_rewards": {
                "5": {"money": 2000, "item": None},
                "10": {"money": 5000, "item": "boost_xp"},
                "15": {"money": 7500, "item": None},
                "20": {"money": 10000, "item": "boost_money"},
                "25": {"money": 15000, "item": "custom_color"},
                "30": {"money": 20000, "item": None},
                "50": {"money": 50000, "item": "premium_role"},
                "75": {"money": 75000, "item": "vip_channel"},
                "100": {"money": 100000, "item": "all_boosts"}
            },
            "work_jobs": [
                {"name": "Développeur", "min": 400, "max": 1000, "description": "Coder des applications"},
                {"name": "Designer", "min": 300, "max": 800, "description": "Créer des designs"},
                {"name": "Streamer", "min": 200, "max": 600, "description": "Diffuser en live"},
                {"name": "YouTubeur", "min": 250, "max": 750, "description": "Créer du contenu vidéo"},
                {"name": "Gamer Pro", "min": 350, "max": 900, "description": "Participer à des tournois"},
                {"name": "Modérateur", "min": 150, "max": 400, "description": "Modérer des serveurs"},
                {"name": "Bot Developer", "min": 500, "max": 1200, "description": "Développer des bots Discord"}
            ],
            "crime_activities": [
                {"name": "Hack un site", "min": 500, "max": 2500, "fail_min": 200, "fail_max": 800},
                {"name": "Vendre des comptes", "min": 300, "max": 1500, "fail_min": 100, "fail_max": 500},
                {"name": "DDoS un serveur", "min": 800, "max": 3000, "fail_min": 400, "fail_max": 1000},
                {"name": "Créer un virus", "min": 1000, "max": 4000, "fail_min": 500, "fail_max": 1500},
                {"name": "Pirater un Discord", "min": 600, "max": 2000, "fail_min": 250, "fail_max": 750}
            ]
        }
    
    def get_user_data(self, user_id: int, guild_id: int) -> dict:
        """Récupère les données d'un utilisateur"""
        user_key = f"{guild_id}_{user_id}"
        if user_key not in self.users_data:
            self.users_data[user_key] = {
                "balance": self.config["starting_balance"],
                "bank": 0,
                "xp": self.config["starting_xp"],
                "level": 1,
                "last_xp_gain": 0,
                "total_earned": self.config["starting_balance"],
                "total_spent": 0,
                "daily_streak": 0,
                "last_daily": 0,
                "last_work": 0,
                "last_crime": 0,
                "inventory": [],
                "active_boosts": {},
                "achievements": [],
                "stats": {
                    "messages_sent": 0,
                    "commands_used": 0,
                    "daily_claims": 0,
                    "work_count": 0,
                    "crime_success": 0,
                    "crime_fail": 0
                }
            }
            self.save_users_data()
        return self.users_data[user_key]
    
    def update_user_data(self, user_id: int, guild_id: int, data: dict):
        """Met à jour les données d'un utilisateur"""
        user_key = f"{guild_id}_{user_id}"
        self.users_data[user_key] = data
        self.save_users_data()
    
    def calculate_level_xp(self, level: int) -> int:
        """Calcule l'XP nécessaire pour un niveau"""
        return level * self.config["level_multiplier"]
    
    def get_level_from_xp(self, xp: int) -> int:
        """Calcule le niveau à partir de l'XP"""
        level = 1
        while xp >= self.calculate_level_xp(level):
            xp -= self.calculate_level_xp(level)
            level += 1
        return level
    
    def get_xp_for_next_level(self, current_xp: int, current_level: int) -> Tuple[int, int]:
        """Retourne (XP actuel dans le niveau, XP nécessaire pour le niveau suivant)"""
        total_xp_for_level = 0
        for i in range(1, current_level):
            total_xp_for_level += self.calculate_level_xp(i)
        
        xp_in_current_level = current_xp - total_xp_for_level
        xp_needed_for_next = self.calculate_level_xp(current_level)
        
        return xp_in_current_level, xp_needed_for_next
    
    async def add_xp(self, user_id: int, guild_id: int, amount: int = None) -> dict:
        """Ajoute de l'XP à un utilisateur"""
        user_data = self.get_user_data(user_id, guild_id)
        
        # Vérifier le cooldown XP
        current_time = time.time()
        if current_time - user_data["last_xp_gain"] < self.config["xp_cooldown"]:
            return {"leveled_up": False, "xp_gained": 0}
        
        # Calculer l'XP à ajouter
        if amount is None:
            xp_config = self.config["xp_per_message"]
            amount = random.randint(xp_config["min"], xp_config["max"])
        
        # Appliquer les boosts XP
        if "boost_xp" in user_data["active_boosts"]:
            boost_data = user_data["active_boosts"]["boost_xp"]
            if current_time < boost_data["expires"]:
                amount = int(amount * boost_data["multiplier"])
            else:
                del user_data["active_boosts"]["boost_xp"]
        
        old_level = user_data["level"]
        user_data["xp"] += amount
        user_data["last_xp_gain"] = current_time
        user_data["stats"]["messages_sent"] += 1
        
        # Calculer le nouveau niveau
        new_level = self.get_level_from_xp(user_data["xp"])
        leveled_up = new_level > old_level
        
        if leveled_up:
            user_data["level"] = new_level
            # Donner les récompenses de niveau
            await self.give_level_rewards(user_id, guild_id, new_level)
        
        self.update_user_data(user_id, guild_id, user_data)
        
        return {
            "leveled_up": leveled_up,
            "old_level": old_level,
            "new_level": new_level,
            "xp_gained": amount
        }
    
    async def give_level_rewards(self, user_id: int, guild_id: int, level: int):
        """Donne les récompenses de niveau"""
        if str(level) in self.config["level_rewards"]:
            reward = self.config["level_rewards"][str(level)]
            user_data = self.get_user_data(user_id, guild_id)
            
            # Donner l'argent
            if reward["money"] > 0:
                user_data["balance"] += reward["money"]
                user_data["total_earned"] += reward["money"]
            
            # Donner l'item
            if reward["item"]:
                await self.give_shop_item(user_id, guild_id, reward["item"])
            
            self.update_user_data(user_id, guild_id, user_data)
    
    async def give_shop_item(self, user_id: int, guild_id: int, item_id: str):
        """Donne un item de la boutique à un utilisateur"""
        if item_id not in self.config["shop_items"]:
            return False
        
        item = self.config["shop_items"][item_id]
        user_data = self.get_user_data(user_id, guild_id)
        current_time = time.time()
        
        if item["type"] == "boost":
            user_data["active_boosts"][item_id] = {
                "multiplier": item["multiplier"],
                "expires": current_time + item["duration"]
            }
        else:
            # Ajouter à l'inventaire
            inventory_item = {
                "id": item_id,
                "name": item["name"],
                "acquired": current_time,
                "expires": current_time + item.get("duration", 0) if item.get("duration") else None
            }
            user_data["inventory"].append(inventory_item)
        
        self.update_user_data(user_id, guild_id, user_data)
        return True
    
    def format_money(self, amount: int) -> str:
        """Formate l'argent avec le symbole"""
        return f"{self.config['currency_symbol']} {amount:,}"
    
    def get_leaderboard(self, guild_id: int, category: str = "level", limit: int = 10) -> List[dict]:
        """Récupère le classement"""
        guild_users = []
        
        for user_key, data in self.users_data.items():
            if user_key.startswith(f"{guild_id}_"):
                user_id = int(user_key.split("_")[1])
                
                if category == "level":
                    value = data["level"]
                elif category == "xp":
                    value = data["xp"]
                elif category == "money":
                    value = data["balance"] + data["bank"]
                elif category == "total_earned":
                    value = data["total_earned"]
                else:
                    continue
                
                guild_users.append({
                    "user_id": user_id,
                    "value": value,
                    "data": data
                })
        
        # Trier par valeur décroissante
        guild_users.sort(key=lambda x: x["value"], reverse=True)
        return guild_users[:limit]

# Commandes slash pour l'économie
economy_group = app_commands.Group(name="economy", description="💰 Système d'économie et de nivellement Arsenal")

@economy_group.command(name="balance", description="💰 Voir votre argent et niveau")
@app_commands.describe(user="Utilisateur à vérifier (optionnel)")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    target_user = user or interaction.user
    user_data = economy.get_user_data(target_user.id, interaction.guild.id)
    
    # Calculer les informations de niveau
    current_xp_in_level, xp_needed_for_next = economy.get_xp_for_next_level(user_data["xp"], user_data["level"])
    progress = (current_xp_in_level / xp_needed_for_next) * 100
    
    embed = discord.Embed(
        title=f"💰 Profil Économique - {target_user.display_name}",
        color=discord.Color.gold()
    )
    
    # Argent
    total_wealth = user_data["balance"] + user_data["bank"]
    embed.add_field(
        name="💵 Argent",
        value=f"**Portefeuille:** {economy.format_money(user_data['balance'])}\n**Banque:** {economy.format_money(user_data['bank'])}\n**Total:** {economy.format_money(total_wealth)}",
        inline=True
    )
    
    # Niveau et XP
    embed.add_field(
        name="🏆 Niveau & XP",
        value=f"**Niveau:** {user_data['level']}\n**XP:** {user_data['xp']:,}\n**Progression:** {progress:.1f}%\n**Prochain niveau:** {xp_needed_for_next - current_xp_in_level:,} XP",
        inline=True
    )
    
    # Statistiques
    embed.add_field(
        name="📊 Statistiques",
        value=f"**Messages:** {user_data['stats']['messages_sent']:,}\n**Daily streak:** {user_data['daily_streak']}\n**Travaux:** {user_data['stats']['work_count']}\n**Crimes réussis:** {user_data['stats']['crime_success']}/{user_data['stats']['crime_success'] + user_data['stats']['crime_fail']}",
        inline=True
    )
    
    # Boosts actifs
    active_boosts = []
    current_time = time.time()
    for boost_id, boost_data in user_data["active_boosts"].items():
        if current_time < boost_data["expires"]:
            remaining = boost_data["expires"] - current_time
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            active_boosts.append(f"**{boost_id}** ({hours}h {minutes}m)")
    
    if active_boosts:
        embed.add_field(
            name="⚡ Boosts Actifs",
            value="\n".join(active_boosts),
            inline=False
        )
    
    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
    embed.set_footer(text=f"Arsenal Economy • Total gagné: {economy.format_money(user_data['total_earned'])}")
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="daily", description="🗓️ Récupérer votre récompense quotidienne")
async def daily_reward(interaction: discord.Interaction):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    current_time = time.time()
    
    # Vérifier le cooldown (24h)
    if current_time - user_data["last_daily"] < 86400:
        remaining = 86400 - (current_time - user_data["last_daily"])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await interaction.response.send_message(f"⏰ Daily déjà récupéré ! Revenez dans {hours}h {minutes}m", ephemeral=True)
        return
    
    # Calculer la récompense
    daily_config = economy.config["daily_reward"]
    base_reward = random.randint(daily_config["min"], daily_config["max"])
    
    # Bonus de streak
    if current_time - user_data["last_daily"] < 172800:  # Moins de 48h
        user_data["daily_streak"] += 1
    else:
        user_data["daily_streak"] = 1
    
    streak_bonus = min(user_data["daily_streak"] * 50, 500)  # Max 500 bonus
    total_reward = base_reward + streak_bonus
    
    # Appliquer les boosts d'argent
    if "boost_money" in user_data["active_boosts"]:
        boost_data = user_data["active_boosts"]["boost_money"]
        if current_time < boost_data["expires"]:
            total_reward = int(total_reward * boost_data["multiplier"])
        else:
            del user_data["active_boosts"]["boost_money"]
    
    # Mettre à jour les données
    user_data["balance"] += total_reward
    user_data["total_earned"] += total_reward
    user_data["last_daily"] = current_time
    user_data["stats"]["daily_claims"] += 1
    
    economy.update_user_data(interaction.user.id, interaction.guild.id, user_data)
    
    embed = discord.Embed(
        title="🗓️ Récompense Quotidienne",
        description=f"**Récompense:** {economy.format_money(total_reward)}",
        color=discord.Color.green()
    )
    
    if streak_bonus > 0:
        embed.add_field(
            name="🔥 Bonus Streak",
            value=f"**Streak:** {user_data['daily_streak']} jours\n**Bonus:** {economy.format_money(streak_bonus)}",
            inline=True
        )
    
    embed.add_field(
        name="💰 Nouveau Solde",
        value=economy.format_money(user_data["balance"]),
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="work", description="💼 Travailler pour gagner de l'argent")
async def work(interaction: discord.Interaction):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    current_time = time.time()
    
    # Vérifier le cooldown (1h)
    if current_time - user_data["last_work"] < 3600:
        remaining = 3600 - (current_time - user_data["last_work"])
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        await interaction.response.send_message(f"⏰ Vous êtes fatigué ! Reposez-vous encore {minutes}m {seconds}s", ephemeral=True)
        return
    
    # Choisir un travail aléatoire
    job = random.choice(economy.config["work_jobs"])
    reward = random.randint(job["min"], job["max"])
    
    # Appliquer les boosts d'argent
    if "boost_money" in user_data["active_boosts"]:
        boost_data = user_data["active_boosts"]["boost_money"]
        if current_time < boost_data["expires"]:
            reward = int(reward * boost_data["multiplier"])
        else:
            del user_data["active_boosts"]["boost_money"]
    
    # Mettre à jour les données
    user_data["balance"] += reward
    user_data["total_earned"] += reward
    user_data["last_work"] = current_time
    user_data["stats"]["work_count"] += 1
    
    economy.update_user_data(interaction.user.id, interaction.guild.id, user_data)
    
    embed = discord.Embed(
        title="💼 Travail Terminé",
        description=f"**Métier:** {job['name']}\n**Tâche:** {job['description']}\n**Gain:** {economy.format_money(reward)}",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💰 Nouveau Solde",
        value=economy.format_money(user_data["balance"]),
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="crime", description="🔫 Commettre un crime (risqué mais lucratif)")
async def crime(interaction: discord.Interaction):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    current_time = time.time()
    
    # Vérifier le cooldown (2h)
    if current_time - user_data["last_crime"] < 7200:
        remaining = 7200 - (current_time - user_data["last_crime"])
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await interaction.response.send_message(f"🚔 Vous êtes surveillé ! Attendez {hours}h {minutes}m", ephemeral=True)
        return
    
    # Choisir un crime aléatoire
    crime_activity = random.choice(economy.config["crime_activities"])
    success = random.random() < economy.config["crime_success_rate"]
    
    if success:
        reward = random.randint(crime_activity["min"], crime_activity["max"])
        
        # Appliquer les boosts d'argent
        if "boost_money" in user_data["active_boosts"]:
            boost_data = user_data["active_boosts"]["boost_money"]
            if current_time < boost_data["expires"]:
                reward = int(reward * boost_data["multiplier"])
            else:
                del user_data["active_boosts"]["boost_money"]
        
        user_data["balance"] += reward
        user_data["total_earned"] += reward
        user_data["stats"]["crime_success"] += 1
        
        embed = discord.Embed(
            title="🔫 Crime Réussi",
            description=f"**Action:** {crime_activity['name']}\n**Gain:** {economy.format_money(reward)}",
            color=discord.Color.dark_green()
        )
        
    else:
        penalty = random.randint(crime_activity["fail_min"], crime_activity["fail_max"])
        penalty = min(penalty, user_data["balance"])  # Ne pas aller en négatif
        
        user_data["balance"] -= penalty
        user_data["stats"]["crime_fail"] += 1
        
        embed = discord.Embed(
            title="🚔 Crime Échoué",
            description=f"**Action:** {crime_activity['name']}\n**Perte:** {economy.format_money(penalty)}",
            color=discord.Color.red()
        )
    
    user_data["last_crime"] = current_time
    economy.update_user_data(interaction.user.id, interaction.guild.id, user_data)
    
    embed.add_field(
        name="💰 Nouveau Solde",
        value=economy.format_money(user_data["balance"]),
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="bank", description="🏦 Gérer votre compte bancaire")
@app_commands.describe(
    action="Action à effectuer",
    amount="Montant (optionnel pour 'balance')"
)
@app_commands.choices(action=[
    app_commands.Choice(name="💰 Voir le solde", value="balance"),
    app_commands.Choice(name="📈 Déposer", value="deposit"),
    app_commands.Choice(name="📉 Retirer", value="withdraw")
])
async def bank(interaction: discord.Interaction, action: str, amount: int = None):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    
    if action == "balance":
        embed = discord.Embed(
            title="🏦 Compte Bancaire",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="💳 Soldes",
            value=f"**Portefeuille:** {economy.format_money(user_data['balance'])}\n**Banque:** {economy.format_money(user_data['bank'])}\n**Total:** {economy.format_money(user_data['balance'] + user_data['bank'])}",
            inline=False
        )
        
        # Calculer les intérêts potentiels
        daily_interest = int(user_data["bank"] * economy.config["bank_interest_rate"])
        if daily_interest > 0:
            embed.add_field(
                name="📈 Intérêts Quotidiens",
                value=f"{economy.format_money(daily_interest)} ({economy.config['bank_interest_rate']*100}%)",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
        return
    
    if amount is None or amount <= 0:
        await interaction.response.send_message("❌ Veuillez spécifier un montant valide", ephemeral=True)
        return
    
    if action == "deposit":
        if user_data["balance"] < amount:
            await interaction.response.send_message("❌ Vous n'avez pas assez d'argent dans votre portefeuille", ephemeral=True)
            return
        
        user_data["balance"] -= amount
        user_data["bank"] += amount
        
        embed = discord.Embed(
            title="🏦 Dépôt Effectué",
            description=f"**Montant déposé:** {economy.format_money(amount)}",
            color=discord.Color.green()
        )
        
    elif action == "withdraw":
        if user_data["bank"] < amount:
            await interaction.response.send_message("❌ Vous n'avez pas assez d'argent à la banque", ephemeral=True)
            return
        
        user_data["bank"] -= amount
        user_data["balance"] += amount
        
        embed = discord.Embed(
            title="🏦 Retrait Effectué",
            description=f"**Montant retiré:** {economy.format_money(amount)}",
            color=discord.Color.orange()
        )
    
    economy.update_user_data(interaction.user.id, interaction.guild.id, user_data)
    
    embed.add_field(
        name="💳 Nouveaux Soldes",
        value=f"**Portefeuille:** {economy.format_money(user_data['balance'])}\n**Banque:** {economy.format_money(user_data['bank'])}",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="shop", description="🛒 Boutique Arsenal - Acheter des items premium")
async def shop(interaction: discord.Interaction):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🛒 Boutique Arsenal",
        description="**Achetez des items premium avec vos Arsenal Coins**",
        color=discord.Color.purple()
    )
    
    for item_id, item in economy.config["shop_items"].items():
        duration_text = ""
        if item.get("duration"):
            days = item["duration"] // 86400
            if days > 0:
                duration_text = f" ({days} jours)"
        
        embed.add_field(
            name=f"{item['name']} - {economy.format_money(item['price'])}",
            value=f"{item['description']}{duration_text}",
            inline=False
        )
    
    embed.add_field(
        name="💡 Comment acheter ?",
        value="Utilisez `/economy buy <item_id>` pour acheter un item",
        inline=False
    )
    
    embed.set_footer(text="Items disponibles: premium_role, custom_color, vip_channel, boost_xp, boost_money")
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="buy", description="🛍️ Acheter un item de la boutique")
@app_commands.describe(item="ID de l'item à acheter")
@app_commands.choices(item=[
    app_commands.Choice(name="🌟 Rôle Premium", value="premium_role"),
    app_commands.Choice(name="🎨 Couleur Personnalisée", value="custom_color"),
    app_commands.Choice(name="💎 Accès VIP", value="vip_channel"),
    app_commands.Choice(name="⚡ Boost XP x2", value="boost_xp"),
    app_commands.Choice(name="💰 Boost Argent x1.5", value="boost_money")
])
async def buy_item(interaction: discord.Interaction, item: str):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    if item not in economy.config["shop_items"]:
        await interaction.response.send_message("❌ Item introuvable", ephemeral=True)
        return
    
    shop_item = economy.config["shop_items"][item]
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    
    # Vérifier si l'utilisateur a assez d'argent
    total_money = user_data["balance"] + user_data["bank"]
    if total_money < shop_item["price"]:
        needed = shop_item["price"] - total_money
        await interaction.response.send_message(f"❌ Pas assez d'argent ! Il vous manque {economy.format_money(needed)}", ephemeral=True)
        return
    
    # Déduire l'argent (d'abord du portefeuille, puis de la banque)
    remaining_cost = shop_item["price"]
    if user_data["balance"] >= remaining_cost:
        user_data["balance"] -= remaining_cost
    else:
        remaining_cost -= user_data["balance"]
        user_data["balance"] = 0
        user_data["bank"] -= remaining_cost
    
    user_data["total_spent"] += shop_item["price"]
    
    # Donner l'item
    success = await economy.give_shop_item(interaction.user.id, interaction.guild.id, item)
    
    if success:
        embed = discord.Embed(
            title="🛍️ Achat Réussi",
            description=f"**Item:** {shop_item['name']}\n**Prix:** {economy.format_money(shop_item['price'])}",
            color=discord.Color.green()
        )
        
        if shop_item["type"] == "boost":
            days = shop_item["duration"] // 86400
            embed.add_field(
                name="⚡ Boost Activé",
                value=f"**Durée:** {days} jours\n**Multiplicateur:** x{shop_item['multiplier']}",
                inline=True
            )
        
        embed.add_field(
            name="💰 Argent Restant",
            value=f"**Portefeuille:** {economy.format_money(user_data['balance'])}\n**Banque:** {economy.format_money(user_data['bank'])}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Erreur lors de l'achat", ephemeral=True)

@economy_group.command(name="inventory", description="🎒 Voir votre inventaire")
async def inventory(interaction: discord.Interaction):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    user_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    current_time = time.time()
    
    embed = discord.Embed(
        title="🎒 Votre Inventaire",
        color=discord.Color.blue()
    )
    
    # Items de l'inventaire
    if user_data["inventory"]:
        inventory_text = []
        for item in user_data["inventory"]:
            if item.get("expires") and current_time > item["expires"]:
                continue  # Item expiré
            
            expire_text = ""
            if item.get("expires"):
                remaining = item["expires"] - current_time
                days = int(remaining // 86400)
                hours = int((remaining % 86400) // 3600)
                expire_text = f" (expire dans {days}j {hours}h)"
            
            inventory_text.append(f"• {item['name']}{expire_text}")
        
        if inventory_text:
            embed.add_field(
                name="📦 Items",
                value="\n".join(inventory_text),
                inline=False
            )
    
    # Boosts actifs
    active_boosts = []
    for boost_id, boost_data in user_data["active_boosts"].items():
        if current_time < boost_data["expires"]:
            remaining = boost_data["expires"] - current_time
            days = int(remaining // 86400)
            hours = int((remaining % 86400) // 3600)
            minutes = int((remaining % 3600) // 60)
            
            if days > 0:
                time_str = f"{days}j {hours}h"
            elif hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            active_boosts.append(f"⚡ **{boost_id}** x{boost_data['multiplier']} ({time_str})")
    
    if active_boosts:
        embed.add_field(
            name="🚀 Boosts Actifs",
            value="\n".join(active_boosts),
            inline=False
        )
    
    if not user_data["inventory"] and not active_boosts:
        embed.description = "Votre inventaire est vide. Visitez la boutique avec `/economy shop`"
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="leaderboard", description="🏆 Classement du serveur")
@app_commands.describe(category="Catégorie de classement")
@app_commands.choices(category=[
    app_commands.Choice(name="🏆 Niveau", value="level"),
    app_commands.Choice(name="⭐ Expérience", value="xp"),
    app_commands.Choice(name="💰 Richesse", value="money"),
    app_commands.Choice(name="📈 Total Gagné", value="total_earned")
])
async def leaderboard(interaction: discord.Interaction, category: str = "level"):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    leaderboard_data = economy.get_leaderboard(interaction.guild.id, category, 10)
    
    if not leaderboard_data:
        await interaction.response.send_message("❌ Aucune donnée disponible", ephemeral=True)
        return
    
    category_names = {
        "level": "🏆 Niveaux",
        "xp": "⭐ Expérience", 
        "money": "💰 Richesse",
        "total_earned": "📈 Total Gagné"
    }
    
    embed = discord.Embed(
        title=f"🏆 Classement - {category_names[category]}",
        color=discord.Color.gold()
    )
    
    leaderboard_text = []
    for i, entry in enumerate(leaderboard_data, 1):
        try:
            user = interaction.client.get_user(entry["user_id"])
            username = user.display_name if user else f"Utilisateur {entry['user_id']}"
        except:
            username = f"Utilisateur {entry['user_id']}"
        
        # Médailles pour le top 3
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        # Formater la valeur
        if category == "money":
            value_str = economy.format_money(entry["value"])
        elif category in ["xp", "total_earned"]:
            value_str = f"{entry['value']:,}"
        else:
            value_str = str(entry["value"])
        
        leaderboard_text.append(f"{medal} **{username}** - {value_str}")
    
    embed.description = "\n".join(leaderboard_text)
    embed.set_footer(text=f"Classement Arsenal Economy • Serveur: {interaction.guild.name}")
    
    await interaction.response.send_message(embed=embed)

@economy_group.command(name="give", description="💸 Donner de l'argent à un autre utilisateur")
@app_commands.describe(
    user="Utilisateur à qui donner l'argent",
    amount="Montant à donner"
)
async def give_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    economy = interaction.client.get_cog('EconomySystem')
    if not economy:
        await interaction.response.send_message("❌ Système économie non chargé", ephemeral=True)
        return
    
    if user.bot:
        await interaction.response.send_message("❌ Vous ne pouvez pas donner d'argent à un bot", ephemeral=True)
        return
    
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ Vous ne pouvez pas vous donner de l'argent à vous-même", ephemeral=True)
        return
    
    if amount <= 0:
        await interaction.response.send_message("❌ Le montant doit être positif", ephemeral=True)
        return
    
    sender_data = economy.get_user_data(interaction.user.id, interaction.guild.id)
    
    if sender_data["balance"] < amount:
        await interaction.response.send_message("❌ Vous n'avez pas assez d'argent dans votre portefeuille", ephemeral=True)
        return
    
    # Transférer l'argent
    sender_data["balance"] -= amount
    economy.update_user_data(interaction.user.id, interaction.guild.id, sender_data)
    
    receiver_data = economy.get_user_data(user.id, interaction.guild.id)
    receiver_data["balance"] += amount
    receiver_data["total_earned"] += amount
    economy.update_user_data(user.id, interaction.guild.id, receiver_data)
    
    embed = discord.Embed(
        title="💸 Transfert Réussi",
        description=f"**De:** {interaction.user.mention}\n**À:** {user.mention}\n**Montant:** {economy.format_money(amount)}",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💰 Votre Nouveau Solde",
        value=economy.format_money(sender_data["balance"]),
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)

class EconomyCog(commands.Cog):
    """Cog pour le système d'économie"""
    
    def __init__(self, bot):
        self.bot = bot
        self.economy = EconomySystem(bot)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Donner de l'XP pour les messages"""
        if message.author.bot or not message.guild:
            return
        
        # Ajouter de l'XP
        result = await self.economy.add_xp(message.author.id, message.guild.id)
        
        # Annoncer les montées de niveau
        if result["leveled_up"]:
            embed = discord.Embed(
                title="🎉 Niveau Supérieur !",
                description=f"**{message.author.mention} a atteint le niveau {result['new_level']} !**",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="⚡ XP Gagné",
                value=f"{result['xp_gained']} XP",
                inline=True
            )
            
            # Vérifier les récompenses de niveau
            if str(result["new_level"]) in self.economy.config["level_rewards"]:
                reward = self.economy.config["level_rewards"][str(result["new_level"])]
                reward_text = []
                if reward["money"] > 0:
                    reward_text.append(f"💰 {self.economy.format_money(reward['money'])}")
                if reward["item"]:
                    item_name = self.economy.config["shop_items"][reward["item"]]["name"]
                    reward_text.append(f"🎁 {item_name}")
                
                if reward_text:
                    embed.add_field(
                        name="🎁 Récompenses",
                        value="\n".join(reward_text),
                        inline=True
                    )
            
            await message.channel.send(embed=embed)

async def setup(bot):
    """Setup du cog économie"""
    await bot.add_cog(EconomyCog(bot))
    
    # Ajouter les commandes slash
    bot.tree.add_command(economy_group)
    
    log.info("💰 Système Économie & Nivellement chargé avec succès")
