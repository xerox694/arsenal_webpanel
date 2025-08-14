#!/usr/bin/env python3
"""
🔧 Script de réparation et mise à jour de la base de données Arsenal V4
"""
import sqlite3
import os

def repair_database():
    """Réparer et mettre à jour la base de données"""
    db_path = "arsenal_v4.db"
    
    print("🔧 Réparation de la base de données Arsenal V4...")
    
    # Si la base existe, l'utiliser sinon en créer une nouvelle
    if os.path.exists(db_path):
        print("📁 Base existante trouvée, mise à jour...")
    else:
        print("🆕 Création d'une nouvelle base...")
    
    # Créer une nouvelle connexion
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer toutes les tables nécessaires
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            discriminator TEXT,
            avatar TEXT,
            access_level TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS servers (
            server_id TEXT PRIMARY KEY,
            server_name TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS connected_servers (
            server_id TEXT PRIMARY KEY,
            server_name TEXT NOT NULL,
            member_count INTEGER DEFAULT 0,
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS user_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            server_id TEXT,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (server_id) REFERENCES servers (server_id)
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            command TEXT,
            server_id TEXT,
            server_name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 1,
            execution_time REAL DEFAULT 0.0,
            parameters TEXT
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS bot_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_type TEXT,
            value INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS panel_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            username TEXT,
            access_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS music_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT,
            song_title TEXT,
            song_url TEXT,
            requested_by TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_playing BOOLEAN DEFAULT 0
        )
        """,
        
        """
        CREATE TABLE IF NOT EXISTS moderation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT,
            moderator_id TEXT,
            target_id TEXT,
            action_type TEXT,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
        """
    ]
    
    # Créer chaque table
    for i, table_sql in enumerate(tables, 1):
        cursor.execute(table_sql)
        print(f"✅ Table {i}/9 créée")
    
    # Insérer des données de test
    print("📊 Insertion de données de test...")
    
    # Serveurs de test
    cursor.execute("""
        INSERT INTO connected_servers (server_id, server_name, member_count, connected_at, last_activity)
        VALUES 
        ('123456789', 'Serveur Arsenal V4', 1337, datetime('now'), datetime('now')),
        ('987654321', 'Test Server', 256, datetime('now'), datetime('now')),
        ('555666777', 'Gaming Community', 789, datetime('now'), datetime('now'))
    """)
    
    # Commandes de test
    cursor.execute("""
        INSERT INTO command_logs (user_id, username, command, server_id, server_name, timestamp, success)
        VALUES 
        ('111222333', 'XeRoX#1234', 'play', '123456789', 'Serveur Arsenal V4', datetime('now', '-5 minutes'), 1),
        ('444555666', 'TestUser#9999', 'skip', '123456789', 'Serveur Arsenal V4', datetime('now', '-3 minutes'), 1),
        ('777888999', 'AdminUser#0001', 'ban', '987654321', 'Test Server', datetime('now', '-1 minute'), 1)
    """)
    
    # Stats de test (ignorer les erreurs)
    try:
        cursor.execute("""
            INSERT INTO bot_stats (stat_type, value, timestamp)
            VALUES 
            ('commands_today', 156, datetime('now')),
            ('users_active', 892, datetime('now')),
            ('music_played', 1247, datetime('now'))
        """)
        print("✅ Stats de test ajoutées")
    except Exception as e:
        print(f"⚠️ Stats ignorées: {e}")
    
    conn.commit()
    conn.close()
    
    print("✅ Base de données réparée avec succès!")
    print(f"📁 Fichier: {os.path.abspath(db_path)}")
    print("🎯 3 serveurs, 3 commandes de test, et stats ajoutées")

if __name__ == "__main__":
    repair_database()
