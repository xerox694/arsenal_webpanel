#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import datetime

def create_creator_accounts():
    """Créer les comptes creator avec 9,999,999,999 ArsenalCoins"""
    
    creator_id = 431359112039890945
    creator_username = "Creator"
    arsenal_coins = 9999999999
    
    print(f"=== CRÉATION COMPTES CREATOR {creator_id} ===")
    
    # 1. hunt_royal_auth.db - hunt_royal_members
    print("\n--- hunt_royal_auth.db ---")
    conn = sqlite3.connect('hunt_royal_auth.db')
    cursor = conn.cursor()
    
    # Vérifier si existe déjà
    cursor.execute('SELECT * FROM hunt_royal_members WHERE discord_id = ?', (str(creator_id),))
    if cursor.fetchone():
        print("Compte déjà existant dans hunt_royal_members")
    else:
        cursor.execute("""
            INSERT INTO hunt_royal_members 
            (discord_id, username, access_token, clan_role, registered_at, last_login, is_active, permissions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(creator_id), creator_username, 'CREATOR_TOKEN_' + str(creator_id), 'admin', 
              datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), 1, 'all_access'))
        conn.commit()
        print("✅ Compte créé dans hunt_royal_members")
    
    conn.close()
    
    # 2. arsenal_v4.db - hunt_royal_accounts (avec coins)
    print("\n--- arsenal_v4.db ---")
    conn = sqlite3.connect('arsenal_v4.db')
    cursor = conn.cursor()
    
    # Vérifier si existe déjà
    cursor.execute('SELECT * FROM hunt_royal_accounts WHERE discord_user_id = ?', (str(creator_id),))
    existing = cursor.fetchone()
    if existing:
        print(f"Compte existant: {existing}")
        # Mettre à jour les coins
        cursor.execute('''
            UPDATE hunt_royal_accounts 
            SET coins = ?, last_updated = ?
            WHERE discord_user_id = ?
        ''', (arsenal_coins, datetime.datetime.now().isoformat(), str(creator_id)))
        conn.commit()
        print(f"✅ Coins mis à jour: {arsenal_coins:,}")
    else:
        cursor.execute("""
            INSERT INTO hunt_royal_accounts 
            (discord_user_id, hunt_royal_id, username, access_code, trophies, level, coins, 
             last_updated, registered_at, is_verified, calculator_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(creator_id), 'CREATOR_HR_' + str(creator_id), creator_username, 'CREATOR_ACCESS', 
              99999, 100, arsenal_coins, datetime.datetime.now().isoformat(), 
              datetime.datetime.now().isoformat(), 1, 1))
        conn.commit()
        print(f"✅ Compte créé dans hunt_royal_accounts avec {arsenal_coins:,} coins")
    
    conn.close()
    
    # 3. hunt_royal_profiles.db - linked_profiles
    print("\n--- hunt_royal_profiles.db ---")
    conn = sqlite3.connect('hunt_royal_profiles.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM linked_profiles WHERE discord_id = ?', (str(creator_id),))
    if cursor.fetchone():
        print("Profil déjà existant dans linked_profiles")
    else:
        cursor.execute("""
            INSERT INTO linked_profiles 
            (discord_id, username, hunt_royal_username, hunt_royal_id, server_region, 
             linked_at, last_updated, profile_data, is_verified, verification_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(creator_id), creator_username, creator_username + '_HR', 'CREATOR_HR_' + str(creator_id), 
              'EU', datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(),
              '{"role": "creator", "admin": true}', 1, 'VERIFIED'))
        conn.commit()
        print("✅ Profil créé dans linked_profiles")
    
    conn.close()
    
    print(f"\n🎉 CREATOR {creator_id} configuré avec {arsenal_coins:,} ArsenalCoins!")

if __name__ == "__main__":
    create_creator_accounts()
