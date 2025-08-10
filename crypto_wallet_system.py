"""
💳 Arsenal V4 - Système Wallet Crypto 
Conversion ArsenalCoins vers crypto/fiat avec commission 1%
Intégration Coinbase pour retraits automatiques
"""

import sqlite3
import json
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid

class CryptoWalletSystem:
    def __init__(self, db_path="crypto_wallets.db"):
        self.db_path = db_path
        self.init_database()
        
        # Configuration des taux et commissions
        self.ARSENAL_COIN_VALUE = Decimal('0.01')  # 1 ArsenalCoin = 0.01€
        self.COMMISSION_RATE = Decimal('0.01')     # 1% commission
        self.OWNER_WALLET_ID = "XEROX_COMMISSION"  # Wallet des commissions
        
        # Intégration Coinbase
        try:
            from coinbase_integration import coinbase_integration
            self.coinbase = coinbase_integration
            self.coinbase_available = True
            print("✅ Intégration Coinbase chargée")
        except Exception as e:
            self.coinbase = None
            self.coinbase_available = False
            print(f"❌ Coinbase non disponible: {e}")
        
    def init_database(self):
        """Initialise la base de données des wallets crypto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des wallets crypto externes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                wallet_address TEXT NOT NULL,
                wallet_type TEXT NOT NULL DEFAULT 'ETH',
                nickname TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des conversions ArsenalCoins -> Crypto/Fiat
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                arsenal_coins_amount INTEGER NOT NULL,
                euro_value DECIMAL(10,2) NOT NULL,
                commission_euro DECIMAL(10,2) NOT NULL,
                final_amount DECIMAL(10,2) NOT NULL,
                destination_wallet TEXT,
                conversion_type TEXT DEFAULT 'WITHDRAW',
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Table des commissions collectées
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commission_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                commission_amount DECIMAL(10,2) NOT NULL,
                source_user_id TEXT NOT NULL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("🏦 Base de données Crypto Wallet initialisée")

    def add_crypto_wallet(self, user_id, wallet_address, wallet_type='ETH', nickname=None):
        """Ajouter un wallet crypto pour un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si le wallet existe déjà
            cursor.execute('''
                SELECT id FROM crypto_wallets 
                WHERE user_id = ? AND wallet_address = ?
            ''', (str(user_id), wallet_address))
            
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Wallet déjà enregistré"}
            
            # Ajouter le nouveau wallet
            cursor.execute('''
                INSERT INTO crypto_wallets 
                (user_id, wallet_address, wallet_type, nickname)
                VALUES (?, ?, ?, ?)
            ''', (str(user_id), wallet_address, wallet_type, nickname))
            
            wallet_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ Wallet crypto ajouté: {user_id} -> {wallet_address}")
            return {
                "success": True, 
                "wallet_id": wallet_id,
                "message": f"Wallet {wallet_type} enregistré avec succès"
            }
            
        except Exception as e:
            print(f"❌ Erreur ajout wallet: {e}")
            return {"success": False, "error": str(e)}

    def get_user_wallets(self, user_id):
        """Récupérer tous les wallets d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, wallet_address, wallet_type, nickname, is_verified, created_at
                FROM crypto_wallets 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (str(user_id),))
            
            wallets = []
            for row in cursor.fetchall():
                wallets.append({
                    "id": row[0],
                    "address": row[1],
                    "type": row[2],
                    "nickname": row[3],
                    "verified": row[4],
                    "created_at": row[5]
                })
            
            conn.close()
            return wallets
            
        except Exception as e:
            print(f"❌ Erreur récupération wallets: {e}")
            return []

    def calculate_conversion(self, arsenal_coins_amount):
        """Calculer la conversion ArsenalCoins -> Euro avec commission"""
        try:
            arsenal_coins = Decimal(str(arsenal_coins_amount))
            
            # Valeur brute en euros
            euro_value = arsenal_coins * self.ARSENAL_COIN_VALUE
            
            # Commission (1%)
            commission = euro_value * self.COMMISSION_RATE
            
            # Montant final après commission
            final_amount = euro_value - commission
            
            return {
                "arsenal_coins": int(arsenal_coins),
                "euro_value": float(euro_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "commission": float(commission.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "final_amount": float(final_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            }
            
        except Exception as e:
            print(f"❌ Erreur calcul conversion: {e}")
            return None

    def request_conversion(self, user_id, arsenal_coins_amount, destination_wallet_id=None, use_coinbase=False):
        """Demander une conversion ArsenalCoins -> Crypto/Fiat"""
        try:
            # Importer et vérifier le solde ArsenalCoins
            from economy_system import EconomyDatabase
            
            eco_db = EconomyDatabase()
            user_wallet = eco_db.get_user_wallet(user_id)
            
            if not user_wallet or user_wallet[2] < arsenal_coins_amount:
                return {
                    "success": False,
                    "error": f"Solde insuffisant. Vous avez {user_wallet[2] if user_wallet else 0} ArsenalCoins"
                }
            
            # Calculer la conversion
            conversion = self.calculate_conversion(arsenal_coins_amount)
            if not conversion:
                return {"success": False, "error": "Erreur de calcul"}
            
            # Générer ID de transaction unique
            transaction_id = f"CONV_{uuid.uuid4().hex[:8]}"
            
            # Récupérer l'adresse wallet de destination
            destination_wallet = None
            conversion_type = "COINBASE" if use_coinbase else "MANUAL"
            
            if destination_wallet_id and not use_coinbase:
                user_wallets = self.get_user_wallets(user_id)
                wallet_found = next((w for w in user_wallets if w["id"] == destination_wallet_id), None)
                if wallet_found:
                    destination_wallet = wallet_found["address"]
            
            # Enregistrer la demande de conversion
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO coin_conversions 
                (transaction_id, user_id, arsenal_coins_amount, euro_value, 
                 commission_euro, final_amount, destination_wallet, conversion_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
            ''', (
                transaction_id, str(user_id), conversion["arsenal_coins"],
                conversion["euro_value"], conversion["commission"], 
                conversion["final_amount"], destination_wallet, conversion_type
            ))
            
            # Débiter les ArsenalCoins immédiatement
            eco_db.update_balance(
                user_id, 
                -arsenal_coins_amount, 
                "CRYPTO_CONVERSION", 
                f"Conversion vers {conversion_type} - Transaction {transaction_id}"
            )
            
            # Enregistrer la commission
            cursor.execute('''
                INSERT INTO commission_earnings 
                (transaction_id, commission_amount, source_user_id)
                VALUES (?, ?, ?)
            ''', (transaction_id, conversion["commission"], str(user_id)))
            
            conn.commit()
            
            # Si Coinbase activé, traiter automatiquement
            coinbase_result = None
            if use_coinbase and self.coinbase_available:
                print(f"🏦 Traitement Coinbase pour {transaction_id}")
                coinbase_result = self.coinbase.process_arsenal_conversion(
                    transaction_id, 
                    conversion["final_amount"]
                )
                
                # Mettre à jour le statut selon le résultat Coinbase
                if coinbase_result["success"]:
                    new_status = "COMPLETED" if coinbase_result.get("status") == "completed" else "PROCESSING"
                    cursor.execute('''
                        UPDATE coin_conversions 
                        SET status = ?, processed_at = CURRENT_TIMESTAMP, 
                            notes = ? 
                        WHERE transaction_id = ?
                    ''', (new_status, json.dumps(coinbase_result), transaction_id))
                else:
                    cursor.execute('''
                        UPDATE coin_conversions 
                        SET status = 'FAILED', processed_at = CURRENT_TIMESTAMP,
                            notes = ?
                        WHERE transaction_id = ?
                    ''', (json.dumps(coinbase_result), transaction_id))
                
                conn.commit()
            
            conn.close()
            
            print(f"✅ Conversion demandée: {user_id} -> {arsenal_coins_amount} AC = {conversion['final_amount']}€")
            
            result = {
                "success": True,
                "transaction_id": transaction_id,
                "conversion": conversion,
                "destination_wallet": destination_wallet,
                "conversion_type": conversion_type,
                "message": f"Conversion de {arsenal_coins_amount} ArsenalCoins demandée avec succès"
            }
            
            if coinbase_result:
                result["coinbase_result"] = coinbase_result
                if coinbase_result["success"]:
                    result["message"] += f" - {('Traitement automatique Coinbase réussi' if coinbase_result.get('status') == 'completed' else 'En cours de traitement Coinbase')}"
                else:
                    result["message"] += " - Erreur traitement Coinbase (traitement manuel requis)"
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur demande conversion: {e}")
            return {"success": False, "error": str(e)}

    def request_coinbase_conversion(self, user_id, arsenal_coins_amount):
        """Conversion directe vers Coinbase (raccourci)"""
        return self.request_conversion(user_id, arsenal_coins_amount, use_coinbase=True)

    def get_conversion_history(self, user_id, limit=20):
        """Récupérer l'historique des conversions d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT transaction_id, arsenal_coins_amount, euro_value, 
                       commission_euro, final_amount, destination_wallet,
                       status, created_at, processed_at
                FROM coin_conversions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (str(user_id), limit))
            
            conversions = []
            for row in cursor.fetchall():
                conversions.append({
                    "transaction_id": row[0],
                    "arsenal_coins": row[1],
                    "euro_value": float(row[2]),
                    "commission": float(row[3]),
                    "final_amount": float(row[4]),
                    "destination_wallet": row[5],
                    "status": row[6],
                    "created_at": row[7],
                    "processed_at": row[8]
                })
            
            conn.close()
            return conversions
            
        except Exception as e:
            print(f"❌ Erreur historique conversions: {e}")
            return []

    def get_commission_stats(self):
        """Récupérer les statistiques des commissions collectées"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total des commissions
            cursor.execute("SELECT COALESCE(SUM(commission_amount), 0) FROM commission_earnings")
            total_commissions = float(cursor.fetchone()[0])
            
            # Commissions aujourd'hui
            cursor.execute('''
                SELECT COALESCE(SUM(commission_amount), 0) 
                FROM commission_earnings 
                WHERE DATE(collected_at) = DATE('now')
            ''')
            today_commissions = float(cursor.fetchone()[0])
            
            # Nombre de conversions
            cursor.execute("SELECT COUNT(*) FROM coin_conversions")
            total_conversions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_commissions": total_commissions,
                "today_commissions": today_commissions,
                "total_conversions": total_conversions,
                "commission_rate": float(self.COMMISSION_RATE * 100)  # En pourcentage
            }
            
        except Exception as e:
            print(f"❌ Erreur stats commissions: {e}")
            return {"total_commissions": 0, "today_commissions": 0, "total_conversions": 0}

# Instance globale
crypto_wallet = CryptoWalletSystem()
