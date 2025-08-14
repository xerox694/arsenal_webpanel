"""
🏦 Arsenal V4 - Système d'Économie RÉEL
Chaque utilisateur Discord a son propre portefeuille
Démarrage à 0€, gain via commandes temporelles
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
import json
import os
from discord.ext import commands

class EconomyDatabase:
    def __init__(self, db_path="economy.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données économie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des portefeuilles utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_wallets (
                discord_id TEXT PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                last_hourly TIMESTAMP,
                last_daily TIMESTAMP,
                last_weekly TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT,
                type TEXT,
                amount INTEGER,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (discord_id) REFERENCES user_wallets (discord_id)
            )
        ''')
        
        # Table des statistiques globales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economy_stats (
                id INTEGER PRIMARY KEY,
                total_money_in_circulation INTEGER DEFAULT 0,
                total_users INTEGER DEFAULT 0,
                total_transactions INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insérer les stats initiales si pas présentes
        cursor.execute('SELECT COUNT(*) FROM economy_stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO economy_stats (id, total_money_in_circulation, total_users, total_transactions)
                VALUES (1, 0, 0, 0)
            ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def get_user_wallet(self, discord_id, username=None):
        """Récupère le portefeuille d'un utilisateur (le crée si inexistant)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_wallets WHERE discord_id = ?', (str(discord_id),))
        wallet = cursor.fetchone()
        
        if not wallet:
            # Créer nouveau portefeuille à 0€
            cursor.execute('''
                INSERT INTO user_wallets (discord_id, username, balance, total_earned, total_spent)
                VALUES (?, ?, 0, 0, 0)
            ''', (str(discord_id), username or f"User_{discord_id}"))
            
            conn.commit()
            wallet = (str(discord_id), username, 0, 0, 0, None, None, None, datetime.now(), datetime.now())
        
        conn.close()
        return wallet
    
    def update_balance(self, discord_id, amount, transaction_type, description):
        """Met à jour le solde d'un utilisateur et enregistre la transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier que l'utilisateur existe
        self.get_user_wallet(discord_id)
        
        # Mettre à jour le solde
        if amount > 0:
            cursor.execute('''
                UPDATE user_wallets 
                SET balance = balance + ?, total_earned = total_earned + ?, updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (amount, amount, str(discord_id)))
        else:
            cursor.execute('''
                UPDATE user_wallets 
                SET balance = balance + ?, total_spent = total_spent + ?, updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (amount, abs(amount), str(discord_id)))
        
        # Enregistrer la transaction
        cursor.execute('''
            INSERT INTO transactions (discord_id, type, amount, description)
            VALUES (?, ?, ?, ?)
        ''', (str(discord_id), transaction_type, amount, description))
        
        # Mettre à jour les stats globales
        cursor.execute('''
            UPDATE economy_stats 
            SET total_money_in_circulation = total_money_in_circulation + ?,
                total_transactions = total_transactions + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (amount,))
        
        conn.commit()
        conn.close()
    
    def can_claim_reward(self, discord_id, reward_type):
        """Vérifie si l'utilisateur peut claim une récompense temporelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'SELECT last_{reward_type} FROM user_wallets WHERE discord_id = ?', (str(discord_id),))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return True
        
        last_claim = datetime.fromisoformat(result[0])
        now = datetime.now()
        
        if reward_type == 'hourly':
            return now - last_claim >= timedelta(hours=1)
        elif reward_type == 'daily':
            return now - last_claim >= timedelta(days=1)
        elif reward_type == 'weekly':
            return now - last_claim >= timedelta(weeks=1)
        
        return False
    
    def claim_reward(self, discord_id, reward_type, username=None):
        """Claim une récompense temporelle"""
        if not self.can_claim_reward(discord_id, reward_type):
            return False, "Récompense déjà réclamée récemment"
        
        # Montants des récompenses
        rewards = {
            'hourly': 50,   # 50€ par heure
            'daily': 500,   # 500€ par jour  
            'weekly': 2000  # 2000€ par semaine
        }
        
        amount = rewards[reward_type]
        
        # Mettre à jour la balance
        self.update_balance(discord_id, amount, f"{reward_type}_reward", f"Récompense {reward_type}")
        
        # Mettre à jour la dernière réclamation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE user_wallets 
            SET last_{reward_type} = CURRENT_TIMESTAMP
            WHERE discord_id = ?
        ''', (str(discord_id),))
        conn.commit()
        conn.close()
        
        return True, f"Récompense {reward_type} réclamée: +{amount}€"
    
    def get_economy_stats(self):
        """Récupère les statistiques globales de l'économie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM economy_stats WHERE id = 1')
        stats = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(*) FROM user_wallets')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(balance) FROM user_wallets')
        circulation = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_money_in_circulation': circulation,
            'total_users': total_users,
            'total_transactions': stats[3] if stats else 0,
            'last_updated': stats[4] if stats else datetime.now()
        }

# Instance globale
economy_db = EconomyDatabase()
