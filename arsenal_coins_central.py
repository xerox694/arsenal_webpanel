#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪙 Arsenal Coins - Système Central v4.2.1
===========================================
Système centralisé pour toutes les transactions ArsenalCoins
Remplace les multiples bases de données séparées par un hub central

Fonctionnalités:
- ✅ Base de données unifiée pour tous les ArsenalCoins
- ✅ Synchronisation automatique entre tous les modules
- ✅ Conversion Coinbase 1 ArsenalCoin = 0.01€ (commission 1%)
- ✅ Audit trail complet de toutes les transactions
- ✅ Support multi-modules (economy, casino, hunt_royal, crypto)
"""

import sqlite3
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArsenalCoinsCentral:
    """
    🏦 Système Central des ArsenalCoins
    
    Cette classe gère TOUTES les opérations ArsenalCoins de manière centralisée.
    Toutes les autres modules doivent passer par cette classe pour :
    - Consulter les soldes
    - Effectuer des transactions
    - Obtenir l'historique
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialiser le système central"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'arsenal_coins_central.db')
        
        self.db_path = db_path
        self.lock = threading.RLock()  # Thread-safe operations
        
        # Initialiser la base de données
        self._init_database()
        
        # Migration automatique depuis les anciennes bases
        self._migrate_old_databases()
        
        logger.info(f"🪙 ArsenalCoins Central initialisé: {db_path}")
    
    def _init_database(self):
        """Créer les tables si elles n'existent pas"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des soldes utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_balances (
                    user_id TEXT PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des transactions (audit trail)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    module_source TEXT NOT NULL,
                    description TEXT,
                    balance_before INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Table des conversions Coinbase
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS coinbase_conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    arsenal_coins INTEGER NOT NULL,
                    euros_amount REAL NOT NULL,
                    commission_euros REAL NOT NULL,
                    coinbase_transaction_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL
                )
            ''')
            
            # Index pour les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON coinbase_conversions(user_id)')
            
            conn.commit()
            conn.close()
    
    def _migrate_old_databases(self):
        """Migrer les données depuis les anciennes bases de données"""
        with self.lock:
            logger.info("🔄 Migration des anciennes bases de données...")
            
            # Bases de données à migrer
            old_dbs = [
                'arsenal_v4.db',
                'hunt_royal.db', 
                'crypto_wallets.db',
                'suggestions.db'
            ]
            
            migrated_count = 0
            
            for db_name in old_dbs:
                db_path = os.path.join(os.path.dirname(__file__), db_name)
                if os.path.exists(db_path):
                    count = self._migrate_from_db(db_path, db_name)
                    migrated_count += count
                    logger.info(f"✅ Migré {count} soldes depuis {db_name}")
            
            if migrated_count > 0:
                logger.info(f"🎉 Migration terminée: {migrated_count} soldes migrés")
            else:
                logger.info("📝 Aucune migration nécessaire")
    
    def _migrate_from_db(self, db_path: str, db_name: str) -> int:
        """Migrer les données d'une base de données spécifique"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Rechercher les tables contenant des soldes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            migrated = 0
            
            for table in tables:
                # Rechercher des colonnes potentielles de solde
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                balance_columns = [col for col in columns if any(term in col.lower() 
                                 for term in ['balance', 'money', 'coins', 'cash'])]
                
                id_columns = [col for col in columns if any(term in col.lower() 
                            for term in ['user_id', 'id', 'discord_id'])]
                
                if balance_columns and id_columns:
                    balance_col = balance_columns[0]
                    id_col = id_columns[0]
                    
                    try:
                        cursor.execute(f"SELECT {id_col}, {balance_col} FROM {table} WHERE {balance_col} > 0")
                        rows = cursor.fetchall()
                        
                        for user_id, balance in rows:
                            if balance and balance > 0:
                                # Ajouter au système central (sans doublon)
                                current_balance = self.get_balance(str(user_id))
                                if current_balance == 0:  # Éviter les doublons
                                    self.add_coins(
                                        str(user_id), 
                                        int(balance), 
                                        f"migration_{db_name}",
                                        f"Migration depuis {db_name}.{table}"
                                    )
                                    migrated += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur migration table {table}: {e}")
            
            conn.close()
            return migrated
            
        except Exception as e:
            logger.error(f"❌ Erreur migration {db_path}: {e}")
            return 0
    
    def get_balance(self, user_id: str) -> int:
        """Obtenir le solde d'un utilisateur"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT balance FROM user_balances WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else 0
    
    def add_coins(self, user_id: str, amount: int, module_source: str, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Ajouter des ArsenalCoins à un utilisateur"""
        if amount <= 0:
            return False
            
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtenir le solde actuel
            current_balance = self.get_balance(user_id)
            new_balance = current_balance + amount
            
            # Mettre à jour ou créer le solde
            cursor.execute('''
                INSERT OR REPLACE INTO user_balances (user_id, balance, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, new_balance))
            
            # Enregistrer la transaction
            cursor.execute('''
                INSERT INTO transactions 
                (user_id, amount, transaction_type, module_source, description, 
                 balance_before, balance_after, metadata)
                VALUES (?, ?, 'add', ?, ?, ?, ?, ?)
            ''', (user_id, amount, module_source, description, 
                  current_balance, new_balance, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💰 +{amount} ArsenalCoins pour {user_id} (module: {module_source})")
            return True
    
    def remove_coins(self, user_id: str, amount: int, module_source: str, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Retirer des ArsenalCoins d'un utilisateur"""
        if amount <= 0:
            return False
            
        current_balance = self.get_balance(user_id)
        if current_balance < amount:
            return False  # Solde insuffisant
            
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_balance = current_balance - amount
            
            # Mettre à jour le solde
            cursor.execute('''
                UPDATE user_balances 
                SET balance = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_balance, user_id))
            
            # Enregistrer la transaction
            cursor.execute('''
                INSERT INTO transactions 
                (user_id, amount, transaction_type, module_source, description, 
                 balance_before, balance_after, metadata)
                VALUES (?, ?, 'remove', ?, ?, ?, ?, ?)
            ''', (user_id, -amount, module_source, description, 
                  current_balance, new_balance, json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💸 -{amount} ArsenalCoins pour {user_id} (module: {module_source})")
            return True
    
    def transfer_coins(self, from_user: str, to_user: str, amount: int, module_source: str, description: Optional[str] = None) -> bool:
        """Transférer des ArsenalCoins entre utilisateurs"""
        if amount <= 0:
            return False
            
        if self.get_balance(from_user) < amount:
            return False  # Solde insuffisant
            
        # Transaction atomique
        with self.lock:
            # Retirer du premier utilisateur
            if not self.remove_coins(from_user, amount, module_source, f"Transfer vers {to_user}: {description}"):
                return False
            
            # Ajouter au deuxième utilisateur
            if not self.add_coins(to_user, amount, module_source, f"Transfer depuis {from_user}: {description}"):
                # Rollback en cas d'erreur
                self.add_coins(from_user, amount, module_source, f"Rollback transfer vers {to_user}")
                return False
            
            logger.info(f"🔄 Transfer {amount} ArsenalCoins: {from_user} → {to_user}")
            return True
    
    def get_transaction_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtenir l'historique des transactions d'un utilisateur"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT amount, transaction_type, module_source, description, 
                       balance_before, balance_after, timestamp, metadata
                FROM transactions 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'amount': row[0],
                    'type': row[1],
                    'module': row[2],
                    'description': row[3],
                    'balance_before': row[4],
                    'balance_after': row[5],
                    'timestamp': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {}
                })
            
            conn.close()
            return transactions
    
    def get_top_users(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Obtenir le classement des utilisateurs les plus riches"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, balance 
                FROM user_balances 
                WHERE balance > 0
                ORDER BY balance DESC
                LIMIT ?
            ''', (limit,))
            
            result = cursor.fetchall()
            conn.close()
            return result
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques globales du système"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total des ArsenalCoins en circulation
            cursor.execute('SELECT SUM(balance) FROM user_balances')
            total_coins = cursor.fetchone()[0] or 0
            
            # Nombre d'utilisateurs avec un solde > 0
            cursor.execute('SELECT COUNT(*) FROM user_balances WHERE balance > 0')
            active_users = cursor.fetchone()[0] or 0
            
            # Total des transactions
            cursor.execute('SELECT COUNT(*) FROM transactions')
            total_transactions = cursor.fetchone()[0] or 0
            
            # Transactions des dernières 24h
            cursor.execute('''
                SELECT COUNT(*) FROM transactions 
                WHERE timestamp > datetime('now', '-1 day')
            ''')
            recent_transactions = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_coins': total_coins,
                'active_users': active_users,
                'total_transactions': total_transactions,
                'recent_transactions': recent_transactions,
                'coinbase_rate': 0.01,  # 1 ArsenalCoin = 0.01€
                'commission_rate': 0.01  # 1% de commission
            }
    
    def create_coinbase_conversion(self, user_id: str, arsenal_coins: int) -> Optional[int]:
        """Créer une demande de conversion Coinbase"""
        if arsenal_coins < 100:  # Minimum 100 ArsenalCoins = 1€
            return None
            
        if self.get_balance(user_id) < arsenal_coins:
            return None  # Solde insuffisant
            
        euros_gross = arsenal_coins * 0.01  # 1 AC = 0.01€
        commission = euros_gross * 0.01  # 1% commission
        euros_net = euros_gross - commission
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO coinbase_conversions 
                (user_id, arsenal_coins, euros_amount, commission_euros)
                VALUES (?, ?, ?, ?)
            ''', (user_id, arsenal_coins, euros_net, commission))
            
            conversion_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"💱 Conversion créée: {arsenal_coins} AC → {euros_net}€ (ID: {conversion_id})")
            return conversion_id
    
    def complete_coinbase_conversion(self, conversion_id: int, coinbase_tx_id: str) -> bool:
        """Finaliser une conversion Coinbase"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtenir les détails de la conversion
            cursor.execute('''
                SELECT user_id, arsenal_coins, status 
                FROM coinbase_conversions 
                WHERE id = ?
            ''', (conversion_id,))
            
            result = cursor.fetchone()
            if not result or result[2] != 'pending':
                conn.close()
                return False
            
            user_id, arsenal_coins, status = result
            
            # Retirer les ArsenalCoins
            if not self.remove_coins(user_id, arsenal_coins, 'coinbase_conversion', 
                                   f"Conversion Coinbase #{conversion_id}"):
                conn.close()
                return False
            
            # Marquer la conversion comme terminée
            cursor.execute('''
                UPDATE coinbase_conversions 
                SET status = 'completed', 
                    coinbase_transaction_id = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (coinbase_tx_id, conversion_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Conversion Coinbase terminée: ID {conversion_id}, TX {coinbase_tx_id}")
            return True

# Instance globale du système central
_central_instance = None

def get_central_system() -> ArsenalCoinsCentral:
    """Obtenir l'instance unique du système central"""
    global _central_instance
    if _central_instance is None:
        _central_instance = ArsenalCoinsCentral()
    return _central_instance

# Fonctions d'interface simplifiées pour compatibilité avec les anciens modules
def get_user_balance(user_id: str) -> int:
    """Interface simple pour obtenir un solde"""
    return get_central_system().get_balance(str(user_id))

def add_user_money(user_id: str, amount: int, source: str = "legacy") -> bool:
    """Interface simple pour ajouter de l'argent"""
    return get_central_system().add_coins(str(user_id), amount, source, f"Legacy add from {source}")

def remove_user_money(user_id: str, amount: int, source: str = "legacy") -> bool:
    """Interface simple pour retirer de l'argent"""
    return get_central_system().remove_coins(str(user_id), amount, source, f"Legacy remove from {source}")

if __name__ == "__main__":
    # Test du système
    print("🧪 Test du système ArsenalCoins Central...")
    
    central = ArsenalCoinsCentral()
    
    # Test avec le créateur (vous)
    creator_id = "431359112039890945"
    
    # Ajouter des coins de test
    central.add_coins(creator_id, 999999999, "system_init", "Coins créateur initial")
    
    # Vérifier le solde
    balance = central.get_balance(creator_id)
    print(f"💰 Solde créateur: {balance:,} ArsenalCoins")
    
    # Statistiques
    stats = central.get_global_stats()
    print(f"📊 Stats: {stats}")
    
    print("✅ Test terminé!")
