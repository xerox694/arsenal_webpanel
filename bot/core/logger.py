import logging
import os
from datetime import datetime

# Configuration du logger
def setup_logger():
    """Configure et retourne le logger pour le bot"""
    
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('ArsenalBot')

# Instance globale du logger
log = setup_logger()

def info(message):
    """Log info message"""
    log.info(message)
    print(f"[INFO] {message}")

def error(message):
    """Log error message"""
    log.error(message)
    print(f"[ERROR] {message}")

def warning(message):
    """Log warning message"""
    log.warning(message)
    print(f"[WARNING] {message}")

def debug(message):
    """Log debug message"""
    log.debug(message)
    print(f"[DEBUG] {message}")
