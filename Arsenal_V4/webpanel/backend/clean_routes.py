#!/usr/bin/env python3
"""
Script pour nettoyer les routes dupliquées dans app.py
"""

def clean_duplicate_routes():
    """Supprime les routes dupliquées du fichier app.py"""
    
    # Lire le fichier
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned_lines = []
    skip_until_line = None
    routes_seen = set()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter les définitions de routes
        if line.strip().startswith('@app.route(') and '/api/auth/user' in line:
            route_name = '/api/auth/user'
            
            if route_name in routes_seen:
                print(f"🔍 Route dupliquée trouvée ligne {i+1}: {route_name}")
                # Ignorer cette route et sa fonction
                while i < len(lines) and not (lines[i].strip().startswith('@app.route(') or 
                                            lines[i].strip().startswith('if __name__') or
                                            lines[i].strip().startswith('# Route') or
                                            lines[i].strip().startswith('def ') and not lines[i-1].strip().startswith('@')):
                    i += 1
                continue
            else:
                routes_seen.add(route_name)
                print(f"✅ Route conservée: {route_name}")
        
        cleaned_lines.append(line)
        i += 1
    
    # Écrire le fichier nettoyé
    cleaned_content = '\n'.join(cleaned_lines)
    
    with open('app_cleaned.py', 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✅ Fichier nettoyé créé: app_cleaned.py")
    print(f"📊 Lignes originales: {len(lines)}")
    print(f"📊 Lignes nettoyées: {len(cleaned_lines)}")

if __name__ == '__main__':
    clean_duplicate_routes()
