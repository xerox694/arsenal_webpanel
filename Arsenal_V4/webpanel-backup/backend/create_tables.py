#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ARSENAL V4 - CRÉATION TABLES BDD COMPLÈTES
Crée toutes les tables pour les 6 phases du webpanel
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = "arsenal_v4.db"

def create_all_tables():
    """Crée toutes les tables nécessaires pour Arsenal V4"""
    print("🔥 ARSENAL V4 - CRÉATION TABLES BDD")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # ================================
    # PHASE 1: TABLES UTILISATEURS
    # ================================
    print("👥 Phase 1: Tables utilisateurs...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            server_id TEXT NOT NULL,
            username TEXT,
            discriminator TEXT,
            avatar_url TEXT,
            join_date TEXT,
            last_activity TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, server_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            server_id TEXT NOT NULL,
            permission_level TEXT DEFAULT 'member',
            roles TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, server_id)
        )
    """)
    
    # ================================
    # PHASE 2: TABLES ÉCONOMIE
    # ================================
    print("💰 Phase 2: Tables économie...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            balance REAL DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            shop_purchases INTEGER DEFAULT 0,
            total_earned REAL DEFAULT 0,
            total_spent REAL DEFAULT 0,
            inventory_items INTEGER DEFAULT 0,
            last_daily TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            available BOOLEAN DEFAULT 1,
            description TEXT,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, item_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            daily_amount REAL DEFAULT 100,
            daily_cooldown INTEGER DEFAULT 24,
            shop_enabled BOOLEAN DEFAULT 1,
            economy_enabled BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ================================
    # PHASE 3: TABLES MODÉRATION
    # ================================
    print("🛡️ Phase 3: Tables modération...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_warns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            moderator_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            severity INTEGER DEFAULT 1,
            resolved BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_bans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            moderator_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            temporary BOOLEAN DEFAULT 0,
            duration_days INTEGER,
            expires_at TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            user_id TEXT,
            moderator_id TEXT,
            reason TEXT,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            auto_mod_enabled BOOLEAN DEFAULT 1,
            warn_threshold INTEGER DEFAULT 3,
            ban_threshold INTEGER DEFAULT 5,
            log_channel_id TEXT,
            mod_role_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ================================
    # PHASE 4: TABLES MUSIQUE
    # ================================
    print("🎵 Phase 4: Tables musique...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 0,
            duration_seconds INTEGER DEFAULT 0,
            added_by TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            played_by TEXT NOT NULL,
            played_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            tracks TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            is_playing BOOLEAN DEFAULT 0,
            current_track TEXT,
            current_position INTEGER DEFAULT 0,
            volume INTEGER DEFAULT 50,
            loop_mode TEXT DEFAULT 'none',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            music_enabled BOOLEAN DEFAULT 1,
            max_queue_size INTEGER DEFAULT 50,
            max_track_duration INTEGER DEFAULT 600,
            dj_role_id TEXT,
            music_channel_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ================================
    # PHASE 5: TABLES GAMING
    # ================================
    print("🎮 Phase 5: Tables gaming...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaming_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            total_xp INTEGER DEFAULT 0,
            prestiges INTEGER DEFAULT 0,
            current_xp INTEGER DEFAULT 0,
            current_level INTEGER DEFAULT 1,
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            achievements_unlocked INTEGER DEFAULT 0,
            last_activity TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, user_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaming_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            reward_id TEXT NOT NULL,
            name TEXT NOT NULL,
            value INTEGER NOT NULL,
            repeatable BOOLEAN DEFAULT 0,
            reward_type TEXT DEFAULT 'xp',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, reward_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaming_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            stat_type TEXT NOT NULL,
            stat_value INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaming_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            gaming_enabled BOOLEAN DEFAULT 1,
            xp_per_message INTEGER DEFAULT 10,
            xp_per_minute_voice INTEGER DEFAULT 5,
            level_up_rewards BOOLEAN DEFAULT 1,
            leaderboard_enabled BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ================================
    # PHASE 6: TABLES ANALYTICS
    # ================================
    print("📊 Phase 6: Tables analytics...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_server_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            date TEXT NOT NULL,
            member_count INTEGER DEFAULT 0,
            messages_count INTEGER DEFAULT 0,
            voice_minutes INTEGER DEFAULT 0,
            commands_used INTEGER DEFAULT 0,
            new_members INTEGER DEFAULT 0,
            left_members INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, date)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_user_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            messages_sent INTEGER DEFAULT 0,
            voice_minutes INTEGER DEFAULT 0,
            commands_used INTEGER DEFAULT 0,
            reactions_added INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(server_id, user_id, date)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            user_id TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            track_messages BOOLEAN DEFAULT 1,
            track_voice BOOLEAN DEFAULT 1,
            track_commands BOOLEAN DEFAULT 1,
            track_reactions BOOLEAN DEFAULT 1,
            retention_days INTEGER DEFAULT 90,
            auto_reports BOOLEAN DEFAULT 0,
            privacy_mode BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ================================
    # TABLES SYSTÈME
    # ================================
    print("⚙️ Tables système...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL UNIQUE,
            server_name TEXT,
            owner_id TEXT,
            prefix TEXT DEFAULT '!',
            language TEXT DEFAULT 'fr',
            timezone TEXT DEFAULT 'UTC',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT,
            level TEXT NOT NULL,
            module TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Commit et fermeture
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ TOUTES LES TABLES CRÉÉES AVEC SUCCÈS!")
    print(f"📊 Base de données: {DATABASE_PATH}")
    print("🎯 Arsenal V4 prêt pour le peuplement de données")

def main():
    """Fonction principale"""
    try:
        create_all_tables()
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")

if __name__ == "__main__":
    main()
