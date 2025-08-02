#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour ajouter le système de freeze aux routes OAuth
"""

def add_freeze_system():
    """Ajouter le système de freeze au fichier app.py"""
    
    # Lire le fichier
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la route /auth/login
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter la route /auth/login
        if '@app.route(\'/auth/login\')' in line and i + 1 < len(lines):
            # Conserver la route
            new_lines.append(line)
            i += 1
            
            # Conserver la définition de fonction
            new_lines.append(lines[i])
            i += 1
            
            # Conserver la docstring
            if i < len(lines) and '"""' in lines[i]:
                new_lines.append(lines[i])
                i += 1
            
            # Ajouter le système de freeze
            new_lines.append('    ')
            new_lines.append('    # 🧊 SYSTÈME DE FREEZE - Créer un freeze pour cette session')
            new_lines.append('    freeze_token = None')
            new_lines.append('    if FREEZE_SYSTEM_AVAILABLE:')
            new_lines.append('        try:')
            new_lines.append('            freeze_token = create_login_freeze(request)')
            new_lines.append('            session[\'freeze_token\'] = freeze_token')
            new_lines.append('            session[\'login_start\'] = datetime.now().isoformat()')
            new_lines.append('            print(f"🧊 FREEZE CRÉÉ: {freeze_token}")')
            new_lines.append('        except Exception as e:')
            new_lines.append('            print(f"⚠️ Erreur création freeze: {e}")')
            new_lines.append('    ')
            
            # Continuer avec le reste du code
            while i < len(lines) and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('if request.args.get'):
                new_lines.append(lines[i])
                i += 1
            
            # Ajouter le reste normalement
            continue
        
        new_lines.append(line)
        i += 1
    
    # Écrire le fichier modifié
    with open('app_with_freeze.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Système de freeze ajouté dans app_with_freeze.py")

if __name__ == '__main__':
    add_freeze_system()
