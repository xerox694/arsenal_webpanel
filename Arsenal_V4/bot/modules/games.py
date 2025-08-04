"""
🎮 Arsenal V4 - Module Jeux et Mini-jeux
=======================================

Module contenant tous les jeux et mini-jeux pour gagner ArsenalCoins et XP
"""

import random
import asyncio
import discord
from discord.ext import commands
from typing import Dict, List
import sqlite3
from datetime import datetime

class GamesModule(commands.Cog):
    """Module de jeux pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Jeux en cours
        
        # Configuration des jeux
        self.game_rewards = {
            'roulette': {'min': 0, 'max': 100, 'multiplier': 2},
            'coinflip': {'min': 10, 'max': 50, 'multiplier': 1.8},
            'dice': {'min': 5, 'max': 30, 'multiplier': 6},
            'blackjack': {'min': 20, 'max': 100, 'multiplier': 2},
            'slots': {'min': 5, 'max': 200, 'multiplier': 10}
        }
    
    @commands.command(name='roulette', aliases=['roul'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def roulette(self, ctx, bet: int = None):
        """🎰 Jeu de roulette - Pariez sur Rouge, Noir ou Vert"""
        
        if bet is None:
            embed = discord.Embed(
                title="🎰 Roulette Arsenal",
                description="Utilisez: `!roulette <mise>`\n\n🔴 Rouge: x2\n⚫ Noir: x2\n🟢 Vert (0): x14",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        user = self.bot.db.get_user(ctx.author.id)
        
        if bet <= 0:
            return await ctx.send("❌ La mise doit être positive !")
        
        if bet > user['balance']:
            return await ctx.send(f"❌ Vous n'avez que {user['balance']:,} ArsenalCoins !")
        
        # Interface de sélection
        embed = discord.Embed(
            title="🎰 Choisissez votre pari",
            description=f"Mise: **{bet:,}** ArsenalCoins",
            color=0xff0000
        )
        
        view = RouletteView(ctx, bet, self.bot)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='coinflip', aliases=['cf', 'flip'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def coinflip(self, ctx, bet: int, choice: str = None):
        """🪙 Pile ou Face - 50/50 de chance"""
        
        if choice is None or choice.lower() not in ['pile', 'face', 'heads', 'tails']:
            embed = discord.Embed(
                title="🪙 Pile ou Face",
                description="Utilisez: `!coinflip <mise> <pile/face>`",
                color=0xf39c12
            )
            return await ctx.send(embed=embed)
        
        user = self.bot.db.get_user(ctx.author.id)
        
        if bet <= 0 or bet > user['balance']:
            return await ctx.send("❌ Mise invalide !")
        
        # Normaliser le choix
        choice = choice.lower()
        if choice in ['heads', 'pile']:
            choice = 'pile'
        else:
            choice = 'face'
        
        # Lancer la pièce
        result = random.choice(['pile', 'face'])
        won = choice == result
        
        if won:
            winnings = int(bet * 1.8)
            self.bot.db.update_balance(ctx.author.id, winnings - bet, f"Coinflip Win: {result}")
            
            embed = discord.Embed(
                title="🎉 Victoire !",
                description=f"La pièce est tombée sur **{result}** !\nVous gagnez **{winnings:,}** ArsenalCoins !",
                color=0x00ff41
            )
        else:
            self.bot.db.update_balance(ctx.author.id, -bet, f"Coinflip Loss: {result}")
            
            embed = discord.Embed(
                title="💔 Défaite !",
                description=f"La pièce est tombée sur **{result}**...\nVous perdez **{bet:,}** ArsenalCoins.",
                color=0xff4757
            )
        
        # Ajouter XP pour avoir joué
        xp_gained = random.randint(3, 8)
        self.bot.db.add_xp(ctx.author.id, xp_gained)
        
        embed.add_field(name="XP Gagné", value=f"+{xp_gained} XP", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='slots', aliases=['slot'])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def slots(self, ctx, bet: int = 10):
        """🎰 Machine à sous Arsenal"""
        
        user = self.bot.db.get_user(ctx.author.id)
        
        if bet <= 0 or bet > user['balance']:
            return await ctx.send("❌ Mise invalide !")
        
        # Symboles de la machine à sous
        symbols = {
            '🍒': {'weight': 30, 'value': 2},
            '🍋': {'weight': 25, 'value': 3},
            '🍊': {'weight': 20, 'value': 4},
            '🍇': {'weight': 15, 'value': 5},
            '💎': {'weight': 8, 'value': 10},
            '👑': {'weight': 2, 'value': 20}
        }
        
        # Générer les rouleaux
        reels = []
        for _ in range(3):
            reel = random.choices(
                list(symbols.keys()),
                weights=[s['weight'] for s in symbols.values()],
                k=1
            )[0]
            reels.append(reel)
        
        # Calculer les gains
        if reels[0] == reels[1] == reels[2]:  # Trois identiques
            multiplier = symbols[reels[0]]['value']
            winnings = bet * multiplier
            profit = winnings - bet
            
            self.bot.db.update_balance(ctx.author.id, profit, f"Slots Jackpot: {reels[0]}")
            
            embed = discord.Embed(
                title="🎰 JACKPOT ! 🎰",
                description=f"🎉 **{' '.join(reels)}** 🎉\n\nVous gagnez **{winnings:,}** ArsenalCoins !",
                color=0x00ff41
            )
        elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:  # Deux identiques
            winnings = int(bet * 1.5)
            profit = winnings - bet
            
            self.bot.db.update_balance(ctx.author.id, profit, "Slots Pair")
            
            embed = discord.Embed(
                title="🎰 Petite victoire !",
                description=f"**{' '.join(reels)}**\n\nVous gagnez **{winnings:,}** ArsenalCoins !",
                color=0xf39c12
            )
        else:  # Aucune combinaison
            self.bot.db.update_balance(ctx.author.id, -bet, "Slots Loss")
            
            embed = discord.Embed(
                title="🎰 Pas de chance...",
                description=f"**{' '.join(reels)}**\n\nVous perdez **{bet:,}** ArsenalCoins.",
                color=0xff4757
            )
        
        # XP pour avoir joué
        xp_gained = random.randint(2, 6)
        self.bot.db.add_xp(ctx.author.id, xp_gained)
        
        embed.add_field(name="XP Gagné", value=f"+{xp_gained} XP", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='quiz')
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def quiz(self, ctx):
        """🧠 Quiz de culture générale"""
        
        questions = [
            {
                "question": "Quelle est la capitale de la France ?",
                "options": ["Paris", "Lyon", "Marseille", "Toulouse"],
                "correct": 0,
                "reward": 25
            },
            {
                "question": "Combien font 2 + 2 ?",
                "options": ["3", "4", "5", "6"],
                "correct": 1,
                "reward": 15
            },
            {
                "question": "Quel est le langage de programmation de Discord.py ?",
                "options": ["JavaScript", "Java", "Python", "C++"],
                "correct": 2,
                "reward": 30
            },
            {
                "question": "En quelle année Discord a-t-il été lancé ?",
                "options": ["2014", "2015", "2016", "2017"],
                "correct": 1,
                "reward": 35
            }
        ]
        
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Quiz Arsenal",
            description=question_data["question"],
            color=0x3498db
        )
        
        for i, option in enumerate(question_data["options"]):
            embed.add_field(
                name=f"{chr(65 + i)}. {option}",
                value="​",  # Caractère invisible
                inline=False
            )
        
        embed.add_field(
            name="Récompense",
            value=f"{question_data['reward']} ArsenalCoins + XP",
            inline=False
        )
        
        view = QuizView(ctx, question_data, self.bot)
        await ctx.send(embed=embed, view=view)

class RouletteView(discord.ui.View):
    """Interface pour le jeu de roulette"""
    
    def __init__(self, ctx, bet: int, bot):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.bet = bet
        self.bot = bot
    
    @discord.ui.button(label="🔴 Rouge", style=discord.ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_roulette(interaction, "rouge")
    
    @discord.ui.button(label="⚫ Noir", style=discord.ButtonStyle.grey)
    async def black_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_roulette(interaction, "noir")
    
    @discord.ui.button(label="🟢 Vert (0)", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_roulette(interaction, "vert")
    
    async def play_roulette(self, interaction: discord.Interaction, choice: str):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Ce n'est pas votre jeu !", ephemeral=True)
            return
        
        # Générer le résultat
        number = random.randint(0, 36)
        
        if number == 0:
            result_color = "vert"
        elif number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
            result_color = "rouge"
        else:
            result_color = "noir"
        
        # Calculer les gains
        if choice == result_color:
            if choice == "vert":
                multiplier = 14
            else:
                multiplier = 2
            
            winnings = self.bet * multiplier
            profit = winnings - self.bet
            
            self.bot.db.update_balance(self.ctx.author.id, profit, f"Roulette Win: {choice}")
            
            embed = discord.Embed(
                title="🎉 Victoire !",
                description=f"Le numéro **{number}** est tombé sur **{result_color}** !\n\nVous gagnez **{winnings:,}** ArsenalCoins !",
                color=0x00ff41
            )
        else:
            self.bot.db.update_balance(self.ctx.author.id, -self.bet, f"Roulette Loss: {result_color}")
            
            embed = discord.Embed(
                title="💔 Défaite !",
                description=f"Le numéro **{number}** est tombé sur **{result_color}**...\n\nVous perdez **{self.bet:,}** ArsenalCoins.",
                color=0xff4757
            )
        
        # XP pour avoir joué
        xp_gained = random.randint(5, 12)
        self.bot.db.add_xp(self.ctx.author.id, xp_gained)
        
        embed.add_field(name="XP Gagné", value=f"+{xp_gained} XP", inline=True)
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

class QuizView(discord.ui.View):
    """Interface pour le quiz"""
    
    def __init__(self, ctx, question_data: dict, bot):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.question_data = question_data
        self.bot = bot
        self.answered = False
        
        # Ajouter les boutons de réponse
        for i, option in enumerate(question_data["options"]):
            button = discord.ui.Button(
                label=f"{chr(65 + i)}. {option}",
                style=discord.ButtonStyle.primary
            )
            button.callback = self.make_answer_callback(i)
            self.add_item(button)
    
    def make_answer_callback(self, option_index: int):
        async def answer_callback(interaction: discord.Interaction):
            if interaction.user != self.ctx.author:
                await interaction.response.send_message("❌ Ce n'est pas votre quiz !", ephemeral=True)
                return
            
            if self.answered:
                await interaction.response.send_message("❌ Vous avez déjà répondu !", ephemeral=True)
                return
            
            self.answered = True
            correct = option_index == self.question_data["correct"]
            
            if correct:
                reward = self.question_data["reward"]
                xp_reward = random.randint(10, 20)
                
                self.bot.db.update_balance(self.ctx.author.id, reward, "Quiz Correct Answer")
                self.bot.db.add_xp(self.ctx.author.id, xp_reward)
                
                embed = discord.Embed(
                    title="🎉 Bonne réponse !",
                    description=f"Vous gagnez **{reward}** ArsenalCoins et **{xp_reward}** XP !",
                    color=0x00ff41
                )
            else:
                correct_answer = self.question_data["options"][self.question_data["correct"]]
                xp_consolation = random.randint(2, 5)
                
                self.bot.db.add_xp(self.ctx.author.id, xp_consolation)
                
                embed = discord.Embed(
                    title="❌ Mauvaise réponse !",
                    description=f"La bonne réponse était: **{correct_answer}**\n\nVous gagnez quand même **{xp_consolation}** XP !",
                    color=0xff4757
                )
            
            # Désactiver tous les boutons
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label.startswith(chr(65 + self.question_data["correct"])):
                        item.style = discord.ButtonStyle.success
                    elif item.label.startswith(chr(65 + option_index)) and not correct:
                        item.style = discord.ButtonStyle.danger
                    item.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
        
        return answer_callback

def setup(bot):
    bot.add_cog(GamesModule(bot))
