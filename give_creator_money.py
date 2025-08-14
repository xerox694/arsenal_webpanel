"""
💰 Script pour donner 9,999,999,999 ArsenalCoins au créateur
"""

import sqlite3
import os
from dotenv import load_dotenv

def give_creator_money():
    load_dotenv()
    
    creator_id = "431359112039890945"  # Votre ID Discord
    arsenal_coins = 9999999999  # 9,999,999,999 ArsenalCoins
    
    print(f"💰 Attribution de {arsenal_coins:,} ArsenalCoins à {creator_id}")
    
    # Bases de données à vérifier
    db_files = [
        "arsenal_v4.db",
        "hunt_royal.db", 
        "Arsenal_V4/webpanel/backend/arsenal_v4.db",
        "crypto_wallets.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Chercher table users/user_economy
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    print(f"📊 Table trouvée: {table_name} dans {db_file}")
                    
                    # Obtenir la structure de la table
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Chercher colonnes d'argent
                    money_columns = [col for col in columns if any(keyword in col.lower() for keyword in ['coin', 'money', 'balance', 'arsenal'])]
                    
                    if money_columns and 'user_id' in columns:
                        # Vérifier si l'utilisateur existe
                        cursor.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", (creator_id,))
                        user = cursor.fetchone()
                        
                        for money_col in money_columns:
                            if user:
                                # Mettre à jour
                                cursor.execute(f"UPDATE {table_name} SET {money_col} = ? WHERE user_id = ?", 
                                             (arsenal_coins, creator_id))
                                print(f"✅ Mis à jour {money_col} = {arsenal_coins:,} dans {table_name}")
                            else:
                                # Créer l'utilisateur
                                if len(columns) >= 3:  # Au moins user_id + 2 autres colonnes
                                    cursor.execute(f"INSERT OR REPLACE INTO {table_name} (user_id, {money_col}) VALUES (?, ?)",
                                                 (creator_id, arsenal_coins))
                                    print(f"✅ Créé utilisateur avec {money_col} = {arsenal_coins:,} dans {table_name}")
                
                conn.commit()
                conn.close()
                print(f"💾 Base {db_file} mise à jour")
                
            except Exception as e:
                print(f"❌ Erreur avec {db_file}: {e}")
        else:
            print(f"⚠️ Base {db_file} introuvable")
    
    print(f"\n🎉 Attribution terminée ! Vous avez maintenant {arsenal_coins:,} ArsenalCoins pour tester !")

if __name__ == "__main__":
    give_creator_money()
