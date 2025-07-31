#!/usr/bin/env python3
"""
Script pour ajouter un utilisateur admin temporaire pour tester l'accès
"""
import sys
import os
sys.path.append('backend')

from sqlite_database import ArsenalDatabase

def add_admin_user():
    """Ajouter un utilisateur admin pour les tests"""
    
    # Remplacez par votre ID Discord
    user_id = input("Entrez votre ID Discord (pour avoir accès au panel): ")
    username = input("Entrez votre nom d'utilisateur Discord: ")
    
    print(f"🔧 Ajout de l'utilisateur {username} ({user_id}) comme admin...")
    
    try:
        db = ArsenalDatabase()
        
        # Ajouter l'utilisateur
        db.add_user(user_id, username, "0000", None)
        
        # Ajouter un serveur de test
        db.execute_query("""
            INSERT OR IGNORE INTO servers (id, name, is_active, owner_id) 
            VALUES (?, ?, 1, ?)
        """, ("123456789", "Serveur Test", user_id))
        
        # Ajouter l'utilisateur au serveur
        db.execute_query("""
            INSERT OR IGNORE INTO user_servers (user_id, server_id, is_member, role) 
            VALUES (?, ?, 1, 'admin')
        """, (user_id, "123456789"))
        
        print("✅ Utilisateur admin ajouté avec succès!")
        print(f"✅ L'utilisateur {username} peut maintenant accéder au panel")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    add_admin_user()
