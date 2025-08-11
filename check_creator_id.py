#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_creator_money():
    """Vérifier ton ID creator et ton argent"""
    
    creator_id = 431359112039890945
    
    # Vérifier arsenal_v4.db
    print("=== ARSENAL_V4.DB ===")
    if os.path.exists('arsenal_v4.db'):
        conn = sqlite3.connect('arsenal_v4.db')
        cursor = conn.cursor()
        
        # Voir les colonnes de users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"Colonnes users: {[col[1] for col in columns]}")
        
        # Voir sample data
        cursor.execute("SELECT * FROM users LIMIT 3")
        sample = cursor.fetchall()
        print(f"Sample data: {sample}")
        
        # Chercher par id (première colonne)
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (creator_id,))
            user = cursor.fetchone()
            if user:
                print(f"Creator trouvé par ID: {user}")
            else:
                print(f"Creator {creator_id} non trouvé par ID")
        except Exception as e:
            print(f"Erreur recherche ID: {e}")
        
        conn.close()
    else:
        print("arsenal_v4.db n'existe pas")
    
    print("\n=== HUNT_ROYAL.DB ===")
    if os.path.exists('hunt_royal.db'):
        conn = sqlite3.connect('hunt_royal.db')
        cursor = conn.cursor()
        
        # Voir les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables hunt_royal: {[t[0] for t in tables]}")
        
        # Chercher dans la table qui existe
        for table_name in [t[0] for t in tables]:
            if 'user' in table_name.lower() or 'economy' in table_name.lower():
                print(f"\n--- Table {table_name} ---")
                try:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    print(f"Colonnes: {[col[1] for col in columns]}")
                    
                    # Voir sample
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample = cursor.fetchall()
                    print(f"Sample: {sample}")
                except Exception as e:
                    print(f"Erreur {table_name}: {e}")
        
        conn.close()
    else:
        print("hunt_royal.db n'existe pas")

if __name__ == "__main__":
    check_creator_money()
