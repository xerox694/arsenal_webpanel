"""
🏦 Arsenal V4 - Intégration Coinbase
Gestion des retraits vers Coinbase et carte bancaire
"""

import requests
import json
import os
import hmac
import hashlib
import time
from datetime import datetime
from decimal import Decimal

class CoinbaseIntegration:
    def __init__(self):
        # Configuration Coinbase (à mettre dans les variables d'environnement)
        self.api_key = os.environ.get('COINBASE_API_KEY')
        self.api_secret = os.environ.get('COINBASE_API_SECRET')
        self.base_url = "https://api.coinbase.com/v2"
        
        # Configuration sandbox pour test
        self.sandbox_mode = os.environ.get('COINBASE_SANDBOX', 'true').lower() == 'true'
        if self.sandbox_mode:
            self.base_url = "https://api.sandbox.coinbase.com/v2"
        
    def generate_signature(self, timestamp, method, path, body=''):
        """Générer la signature pour l'authentification Coinbase"""
        try:
            message = timestamp + method + path + body
            signature = hmac.new(
                self.api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            print(f"❌ Erreur signature Coinbase: {e}")
            return None

    def get_headers(self, method, path, body=''):
        """Obtenir les headers d'authentification"""
        timestamp = str(int(time.time()))
        signature = self.generate_signature(timestamp, method, path, body)
        
        return {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-VERSION': '2024-08-10',
            'Content-Type': 'application/json'
        }

    def test_connection(self):
        """Tester la connexion à l'API Coinbase"""
        try:
            if not self.api_key or not self.api_secret:
                return {
                    "success": False,
                    "error": "Clés API Coinbase manquantes",
                    "sandbox": self.sandbox_mode
                }
            
            headers = self.get_headers('GET', '/user')
            response = requests.get(f"{self.base_url}/user", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "user": data.get('data', {}),
                    "sandbox": self.sandbox_mode
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur API: {response.status_code}",
                    "response": response.text[:200]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_accounts(self):
        """Récupérer les comptes Coinbase"""
        try:
            headers = self.get_headers('GET', '/accounts')
            response = requests.get(f"{self.base_url}/accounts", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                accounts = []
                
                for account in data.get('data', []):
                    accounts.append({
                        "id": account.get('id'),
                        "name": account.get('name'),
                        "currency": account.get('currency'),
                        "balance": account.get('balance', {}).get('amount', '0'),
                        "type": account.get('type'),
                        "primary": account.get('primary', False)
                    })
                
                return {"success": True, "accounts": accounts}
            else:
                return {
                    "success": False,
                    "error": f"Erreur récupération comptes: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_eur_wallet(self):
        """Créer ou récupérer le wallet EUR"""
        try:
            # D'abord essayer de récupérer le wallet EUR existant
            accounts = self.get_accounts()
            if accounts["success"]:
                for account in accounts["accounts"]:
                    if account["currency"] == "EUR" and account["type"] == "wallet":
                        return {
                            "success": True,
                            "wallet_id": account["id"],
                            "balance": account["balance"],
                            "existing": True
                        }
            
            # Si pas de wallet EUR, en créer un
            headers = self.get_headers('POST', '/accounts')
            data = {
                "name": "Arsenal EUR Wallet",
                "currency": "EUR"
            }
            
            response = requests.post(
                f"{self.base_url}/accounts", 
                headers=headers, 
                json=data
            )
            
            if response.status_code == 201:
                account_data = response.json().get('data', {})
                return {
                    "success": True,
                    "wallet_id": account_data.get('id'),
                    "balance": "0.00",
                    "existing": False
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur création wallet: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def deposit_to_coinbase(self, amount_eur, transaction_reference):
        """Déposer des euros vers Coinbase (simulation)"""
        try:
            # En production, ceci ferait un vrai dépôt vers Coinbase
            # Pour l'instant, on simule et on log
            
            wallet_result = self.create_eur_wallet()
            if not wallet_result["success"]:
                return wallet_result
            
            wallet_id = wallet_result["wallet_id"]
            
            # Simuler le dépôt (en sandbox mode)
            if self.sandbox_mode:
                print(f"💰 [SIMULATION] Dépôt {amount_eur}€ vers Coinbase wallet {wallet_id}")
                print(f"📄 [SIMULATION] Référence: {transaction_reference}")
                
                return {
                    "success": True,
                    "coinbase_transaction_id": f"sim_{transaction_reference}",
                    "wallet_id": wallet_id,
                    "amount": amount_eur,
                    "currency": "EUR",
                    "status": "completed",
                    "simulation": True
                }
            
            # En production, utiliser l'API réelle
            headers = self.get_headers('POST', f'/accounts/{wallet_id}/deposits')
            data = {
                "amount": str(amount_eur),
                "currency": "EUR",
                "commit": True,
                "description": f"Arsenal conversion - {transaction_reference}"
            }
            
            response = requests.post(
                f"{self.base_url}/accounts/{wallet_id}/deposits",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                transaction_data = response.json().get('data', {})
                return {
                    "success": True,
                    "coinbase_transaction_id": transaction_data.get('id'),
                    "wallet_id": wallet_id,
                    "amount": amount_eur,
                    "currency": "EUR",
                    "status": transaction_data.get('status'),
                    "simulation": False
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur dépôt: {response.status_code}",
                    "response": response.text[:200]
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def withdraw_to_bank_card(self, amount_eur, payment_method_id=None):
        """Retirer vers la carte bancaire connectée"""
        try:
            wallet_result = self.create_eur_wallet()
            if not wallet_result["success"]:
                return wallet_result
                
            wallet_id = wallet_result["wallet_id"]
            
            # Si pas de méthode de paiement spécifiée, utiliser la première disponible
            if not payment_method_id:
                payment_methods = self.get_payment_methods()
                if payment_methods["success"] and payment_methods["methods"]:
                    # Chercher une carte bancaire
                    for method in payment_methods["methods"]:
                        if method["type"] in ["fiat_account", "bank_wire", "sepa_bank_account"]:
                            payment_method_id = method["id"]
                            break
                
                if not payment_method_id:
                    return {
                        "success": False,
                        "error": "Aucune méthode de paiement trouvée"
                    }
            
            # Simuler le retrait en sandbox
            if self.sandbox_mode:
                print(f"💳 [SIMULATION] Retrait {amount_eur}€ vers carte bancaire")
                print(f"🏦 [SIMULATION] Méthode: {payment_method_id}")
                
                return {
                    "success": True,
                    "withdrawal_id": f"sim_withdrawal_{int(time.time())}",
                    "amount": amount_eur,
                    "currency": "EUR",
                    "status": "completed",
                    "payment_method": payment_method_id,
                    "simulation": True,
                    "estimated_arrival": "1-2 jours ouvrés"
                }
            
            # Retrait réel en production
            headers = self.get_headers('POST', f'/accounts/{wallet_id}/withdrawals')
            data = {
                "amount": str(amount_eur),
                "currency": "EUR",
                "payment_method": payment_method_id,
                "commit": True
            }
            
            response = requests.post(
                f"{self.base_url}/accounts/{wallet_id}/withdrawals",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                withdrawal_data = response.json().get('data', {})
                return {
                    "success": True,
                    "withdrawal_id": withdrawal_data.get('id'),
                    "amount": amount_eur,
                    "currency": "EUR",
                    "status": withdrawal_data.get('status'),
                    "payment_method": payment_method_id,
                    "simulation": False
                }
            else:
                return {
                    "success": False,
                    "error": f"Erreur retrait: {response.status_code}",
                    "response": response.text[:200]
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_payment_methods(self):
        """Récupérer les méthodes de paiement disponibles"""
        try:
            headers = self.get_headers('GET', '/payment-methods')
            response = requests.get(f"{self.base_url}/payment-methods", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                methods = []
                
                for method in data.get('data', []):
                    methods.append({
                        "id": method.get('id'),
                        "type": method.get('type'),
                        "name": method.get('name'),
                        "currency": method.get('currency'),
                        "verified": method.get('verified', False),
                        "allow_withdraw": method.get('allow_withdraw', False)
                    })
                
                return {"success": True, "methods": methods}
            else:
                return {
                    "success": False,
                    "error": f"Erreur méthodes de paiement: {response.status_code}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_arsenal_conversion(self, arsenal_transaction_id, amount_eur):
        """Traiter une conversion Arsenal complète"""
        try:
            print(f"🏦 Traitement conversion Coinbase: {arsenal_transaction_id} -> {amount_eur}€")
            
            # Étape 1: Déposer vers Coinbase
            deposit_result = self.deposit_to_coinbase(amount_eur, arsenal_transaction_id)
            if not deposit_result["success"]:
                return {
                    "success": False,
                    "step": "deposit",
                    "error": deposit_result["error"]
                }
            
            # Étape 2: Retirer vers carte bancaire
            withdrawal_result = self.withdraw_to_bank_card(amount_eur)
            if not withdrawal_result["success"]:
                return {
                    "success": False,
                    "step": "withdrawal",
                    "error": withdrawal_result["error"],
                    "deposit_id": deposit_result.get("coinbase_transaction_id")
                }
            
            return {
                "success": True,
                "deposit": deposit_result,
                "withdrawal": withdrawal_result,
                "total_amount": amount_eur,
                "status": "completed" if self.sandbox_mode else "processing"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Instance globale
coinbase_integration = CoinbaseIntegration()
