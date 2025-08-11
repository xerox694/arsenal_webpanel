#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def scan_all_databases():
    """Scanner toutes les DB pour trouver ton creator ID"""
    
    creator_id = 431359112039890945
    
    # Chercher dans toutes les DB
    for db_file in ['arsenal_v4.db', 'hunt_royal.db', 'hunt_royal_auth.db', 'hunt_royal_profiles.db']:
        if os.path.exists(db_file):
            print(f'\n=== {db_file.upper()} ===')
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                
                # Chercher les colonnes intéressantes
                if any(col in col_names for col in ['discord_id', 'user_id', 'arsenal_coins', 'coins']):
                    print(f'\nTable: {table_name}')
                    print(f'  Colonnes: {col_names}')
                    
                    # Voir sample data
                    cursor.execute(f'SELECT * FROM {table_name} LIMIT 2')
                    sample = cursor.fetchall()
                    if sample:
                        print(f'  Sample: {sample}')
                    
                    # Chercher le creator ID
                    for col in ['discord_id', 'user_id', 'id']:
                        if col in col_names:
                            try:
                                cursor.execute(f'SELECT * FROM {table_name} WHERE {col} = ?', (creator_id,))
                                result = cursor.fetchone()
                                if result:
                                    print(f'  *** CREATOR TROUVÉ dans {col}: {result}')
                                    break
                            except Exception as e:
                                print(f'  Erreur recherche {col}: {e}')
            
            conn.close()

if __name__ == "__main__":
    scan_all_databases()
