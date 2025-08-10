#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💎 ARSENAL V4 - SYSTÈME CRYPTO & PORTEFEUILLES
Conversion ArsenalCoins vers cryptos, QR codes, transferts instantanés
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import asyncio
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from PIL import Image, ImageDraw, ImageFont
import os
from core.logger import log

class CryptoSystem:
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "crypto_wallets.db"
        self.config_path = "data/crypto_config.json"
        self.commission_rate = 0.01  # 1% de commission
        self.conversion_rates = {
            "EUR": 0.01,  # 1 ArsenalCoin = 0.01€
            "ETH": 0.000004,  # Exemple: 1 AC = 0.000004 ETH
            "BTC": 0.0000002,  # Exemple: 1 AC = 0.0000002 BTC
            "BNB": 0.00002,   # Exemple: 1 AC = 0.00002 BNB
            "MATIC": 0.01     # Exemple: 1 AC = 0.01 MATIC
        }
        self.init_database()
        self.load_config()
        
    def init_database(self):
        """Initialise la base de données crypto"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des portefeuilles utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_wallets (
                    user_id INTEGER PRIMARY KEY,
                    eth_address TEXT,
                    btc_address TEXT,
                    bnb_address TEXT,
                    matic_address TEXT,
                    coinbase_email TEXT,
                    coinbase_wallet_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des conversions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount_ac INTEGER,
                    crypto_type TEXT,
                    crypto_amount REAL,
                    commission REAL,
                    wallet_address TEXT,
                    status TEXT DEFAULT 'pending',
                    transaction_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            ''')
            
            # Table des transferts instantanés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS instant_transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER,
                    receiver_id INTEGER,
                    amount_ac INTEGER,
                    qr_code_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    claimed_at TIMESTAMP
                )
            ''')
            
            # Table des QR codes générés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS qr_codes (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    type TEXT,  -- 'wallet_address' ou 'instant_transfer'
                    data TEXT,  -- Adresse wallet ou ID de transfert
                    amount_ac INTEGER DEFAULT 0,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            log.info("💎 Base de données crypto initialisée")
            
        except Exception as e:
            log.error(f"❌ Erreur init DB crypto: {e}")
    
    def load_config(self):
        """Charge la configuration crypto"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                log.info("💎 Configuration crypto chargée")
            except Exception as e:
                log.error(f"❌ Erreur chargement crypto config: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "enabled": True,
            "min_conversion": 100,  # Minimum 100 AC pour convertir
            "max_conversion": 1000000,  # Maximum 1M AC
            "commission_rate": 0.01,
            "instant_transfer_enabled": True,
            "qr_code_expiry_hours": 24,
            "supported_cryptos": ["ETH", "BTC", "BNB", "MATIC"],
            "coinbase_integration": True
        }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde crypto config: {e}")
    
    def generate_qr_code(self, data: str, qr_type: str = "text") -> io.BytesIO:
        """Génère un QR code stylisé Arsenal"""
        try:
            # Configuration QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Couleurs Arsenal
            fill_color = "#00ff88"  # Vert Arsenal
            back_color = "#1a1a1a"  # Noir Arsenal
            
            # Créer l'image QR
            qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Créer une image plus grande avec logo
            final_size = (400, 450)
            final_img = Image.new('RGB', final_size, back_color)
            
            # Redimensionner le QR code
            qr_resized = qr_img.resize((350, 350))
            
            # Coller le QR code centré
            final_img.paste(qr_resized, (25, 25))
            
            # Ajouter le texte Arsenal en bas
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            text = "🎯 ARSENAL V4 CRYPTO"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (final_size[0] - text_width) // 2
            draw.text((text_x, 390), text, fill=fill_color, font=font)
            
            # Convertir en bytes
            img_bytes = io.BytesIO()
            final_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            log.error(f"❌ Erreur génération QR code: {e}")
            return None
    
    def create_wallet_qr(self, user_id: int, crypto_type: str, address: str) -> str:
        """Crée un QR code pour une adresse wallet"""
        try:
            # Générer un ID unique
            qr_id = f"wallet_{user_id}_{crypto_type}_{int(datetime.now().timestamp())}"
            
            # Données du QR code
            qr_data = {
                "type": "wallet_address",
                "crypto": crypto_type,
                "address": address,
                "user_id": user_id,
                "arsenal_id": qr_id
            }
            
            # Enregistrer en DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=self.config["qr_code_expiry_hours"])
            
            cursor.execute('''
                INSERT INTO qr_codes (id, user_id, type, data, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (qr_id, user_id, "wallet_address", json.dumps(qr_data), expires_at))
            
            conn.commit()
            conn.close()
            
            return qr_id
            
        except Exception as e:
            log.error(f"❌ Erreur création QR wallet: {e}")
            return None
    
    def create_instant_transfer_qr(self, sender_id: int, amount_ac: int) -> str:
        """Crée un QR code pour un transfert instantané"""
        try:
            # Générer un ID unique
            qr_id = f"transfer_{sender_id}_{amount_ac}_{int(datetime.now().timestamp())}"
            
            # Données du QR code
            qr_data = {
                "type": "instant_transfer",
                "sender_id": sender_id,
                "amount_ac": amount_ac,
                "arsenal_id": qr_id
            }
            
            # Enregistrer en DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=1)  # Transferts expirent en 1h
            
            cursor.execute('''
                INSERT INTO qr_codes (id, user_id, type, data, amount_ac, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (qr_id, sender_id, "instant_transfer", json.dumps(qr_data), amount_ac, expires_at))
            
            # Créer l'entrée de transfert
            cursor.execute('''
                INSERT INTO instant_transfers (sender_id, amount_ac, qr_code_id)
                VALUES (?, ?, ?)
            ''', (sender_id, amount_ac, qr_id))
            
            conn.commit()
            conn.close()
            
            return qr_id
            
        except Exception as e:
            log.error(f"❌ Erreur création QR transfert: {e}")
            return None
    
    def scan_qr_code(self, qr_id: str, user_id: int) -> Dict:
        """Traite un QR code scanné"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Récupérer le QR code
            cursor.execute('''
                SELECT * FROM qr_codes WHERE id = ? AND expires_at > datetime('now')
            ''', (qr_id,))
            
            qr_result = cursor.fetchone()
            if not qr_result:
                return {"success": False, "error": "QR code invalide ou expiré"}
            
            qr_data = json.loads(qr_result[3])  # data column
            
            if qr_data["type"] == "wallet_address":
                # QR code d'adresse wallet
                return {
                    "success": True,
                    "type": "wallet_address",
                    "crypto": qr_data["crypto"],
                    "address": qr_data["address"],
                    "owner_id": qr_data["user_id"]
                }
                
            elif qr_data["type"] == "instant_transfer":
                # QR code de transfert instantané
                if qr_data["sender_id"] == user_id:
                    return {"success": False, "error": "Vous ne pouvez pas scanner votre propre QR de transfert"}
                
                # Vérifier si déjà réclamé
                cursor.execute('''
                    SELECT * FROM instant_transfers 
                    WHERE qr_code_id = ? AND status = 'pending'
                ''', (qr_id,))
                
                transfer = cursor.fetchone()
                if not transfer:
                    return {"success": False, "error": "Transfert déjà réclamé ou invalide"}
                
                return {
                    "success": True,
                    "type": "instant_transfer",
                    "sender_id": qr_data["sender_id"],
                    "amount_ac": qr_data["amount_ac"],
                    "transfer_id": transfer[0]
                }
            
            conn.close()
            return {"success": False, "error": "Type de QR code non reconnu"}
            
        except Exception as e:
            log.error(f"❌ Erreur scan QR code: {e}")
            return {"success": False, "error": f"Erreur: {e}"}
    
    def claim_instant_transfer(self, transfer_id: int, receiver_id: int) -> Dict:
        """Réclame un transfert instantané"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Récupérer le transfert
            cursor.execute('''
                SELECT * FROM instant_transfers 
                WHERE id = ? AND status = 'pending'
            ''', (transfer_id,))
            
            transfer = cursor.fetchone()
            if not transfer:
                return {"success": False, "error": "Transfert introuvable ou déjà réclamé"}
            
            sender_id = transfer[1]
            amount_ac = transfer[3]
            
            # Vérifier que l'expéditeur a assez d'ArsenalCoins
            from modules.economy_system import EconomySystem
            economy = EconomySystem(self.bot)
            
            sender_balance = economy.get_user_money(sender_id)
            if sender_balance < amount_ac:
                return {"success": False, "error": "L'expéditeur n'a plus assez d'ArsenalCoins"}
            
            # Effectuer le transfert
            economy.remove_money(sender_id, amount_ac)
            economy.add_money(receiver_id, amount_ac)
            
            # Marquer comme réclamé
            cursor.execute('''
                UPDATE instant_transfers 
                SET receiver_id = ?, status = 'claimed', claimed_at = datetime('now')
                WHERE id = ?
            ''', (receiver_id, transfer_id))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "amount_ac": amount_ac
            }
            
        except Exception as e:
            log.error(f"❌ Erreur réclamation transfert: {e}")
            return {"success": False, "error": f"Erreur: {e}"}
    
    def get_user_crypto_stats(self, user_id: int) -> Dict:
        """Statistiques crypto d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Portefeuilles
            cursor.execute('SELECT * FROM user_wallets WHERE user_id = ?', (user_id,))
            wallet = cursor.fetchone()
            
            # Conversions
            cursor.execute('''
                SELECT COUNT(*), SUM(amount_ac), SUM(commission)
                FROM conversions WHERE user_id = ?
            ''', (user_id,))
            conversion_stats = cursor.fetchone()
            
            # Transferts envoyés
            cursor.execute('''
                SELECT COUNT(*), SUM(amount_ac)
                FROM instant_transfers WHERE sender_id = ? AND status = 'claimed'
            ''', (user_id,))
            sent_stats = cursor.fetchone()
            
            # Transferts reçus
            cursor.execute('''
                SELECT COUNT(*), SUM(amount_ac)
                FROM instant_transfers WHERE receiver_id = ? AND status = 'claimed'
            ''', (user_id,))
            received_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                "has_wallet": wallet is not None,
                "wallets": {
                    "eth": wallet[2] if wallet else None,
                    "btc": wallet[3] if wallet else None,
                    "bnb": wallet[4] if wallet else None,
                    "matic": wallet[5] if wallet else None,
                    "coinbase": wallet[6] if wallet else None
                },
                "conversions": {
                    "total": conversion_stats[0] or 0,
                    "total_ac": conversion_stats[1] or 0,
                    "total_commission": conversion_stats[2] or 0
                },
                "transfers": {
                    "sent_count": sent_stats[0] or 0,
                    "sent_amount": sent_stats[1] or 0,
                    "received_count": received_stats[0] or 0,
                    "received_amount": received_stats[1] or 0
                }
            }
            
        except Exception as e:
            log.error(f"❌ Erreur stats crypto: {e}")
            return None
    
    def cleanup_expired_qr_codes(self):
        """Nettoie les QR codes expirés"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Supprimer les QR codes expirés
            cursor.execute("DELETE FROM qr_codes WHERE expires_at < datetime('now')")
            
            # Marquer les transferts expirés comme annulés
            cursor.execute('''
                UPDATE instant_transfers 
                SET status = 'expired' 
                WHERE qr_code_id IN (
                    SELECT id FROM qr_codes WHERE expires_at < datetime('now')
                ) AND status = 'pending'
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            log.error(f"❌ Erreur nettoyage QR codes: {e}")

# Fonction d'initialisation pour le bot
def setup(bot):
    return CryptoSystem(bot)
