#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter le système de freeze aux routes OAuth callback
"""

def add_callback_freeze():
    """Ajouter le système de freeze au callback"""
    
    # Lire le fichier modifié
    with open('app_with_freeze.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la route /auth/callback
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter la route /auth/callback
        if 'def discord_callback():' in line:
            # Conserver la définition de fonction
            new_lines.append(line)
            i += 1
            
            # Conserver la docstring et autres lignes jusqu'au try/except principal
            while i < len(lines) and 'try:' not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            
            # Ajouter le try
            new_lines.append(lines[i])  # try:
            i += 1
            
            # Ajouter le système de freeze au début du try
            new_lines.append('        # 🧊 RÉCUPÉRATION DU FREEZE TOKEN')
            new_lines.append('        freeze_token = session.get(\'freeze_token\')')
            new_lines.append('        print(f"🧊 CALLBACK - Freeze token: {freeze_token}")')
            new_lines.append('        ')
            
            # Continuer avec le reste du code
            continue
        
        new_lines.append(line)
        i += 1
    
    # Écrire le fichier final
    with open('app_final.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Système de freeze callback ajouté dans app_final.py")

if __name__ == '__main__':
    add_callback_freeze()
