"""
🔔 Arsenal V4 - Système de Notifications Push
Notifications en temps réel pour le webpanel
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

class ArsenalNotificationSystem:
    def __init__(self):
        self.subscribers = {}  # WebSocket connections
        self.notification_queue = []
        self.notification_history = []
        self.running = False
        
    def start(self):
        """Démarrer le système de notifications"""
        self.running = True
        self.notification_thread = threading.Thread(target=self._notification_loop, daemon=True)
        self.notification_thread.start()
        print("🔔 Système de notifications démarré")
        
    def stop(self):
        """Arrêter le système"""
        self.running = False
        print("⏹️ Système de notifications arrêté")
        
    def _notification_loop(self):
        """Boucle principale des notifications"""
        while self.running:
            try:
                # Vérifier s'il y a des notifications à envoyer
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    self._broadcast_notification(notification)
                    
                # Générer des notifications automatiques périodiques
                self._generate_auto_notifications()
                
                time.sleep(5)  # Check toutes les 5 secondes
                
            except Exception as e:
                print(f"❌ Erreur notification loop: {e}")
                time.sleep(10)
                
    def _generate_auto_notifications(self):
        """Générer des notifications automatiques"""
        current_time = time.time()
        
        # Notification de monitoring système (toutes les 5 minutes)
        if not hasattr(self, '_last_system_check') or current_time - self._last_system_check > 300:
            self._last_system_check = current_time
            self.add_notification({
                'type': 'system',
                'title': '🔍 Monitoring Système',
                'message': 'Vérification système automatique effectuée',
                'priority': 'low',
                'auto_generated': True
            })
            
        # Notification de santé du bot (toutes les 2 minutes)
        if not hasattr(self, '_last_bot_check') or current_time - self._last_bot_check > 120:
            self._last_bot_check = current_time
            self.add_notification({
                'type': 'bot_status',
                'title': '🤖 Bot Status',
                'message': 'Bot Arsenal opérationnel - 3 serveurs connectés',
                'priority': 'info',
                'auto_generated': True
            })
    
    def add_notification(self, notification_data):
        """Ajouter une nouvelle notification"""
        notification = {
            'id': f"notif_{int(time.time())}_{len(self.notification_queue)}",
            'timestamp': time.time(),
            'read': False,
            'type': notification_data.get('type', 'info'),
            'title': notification_data.get('title', 'Notification'),
            'message': notification_data.get('message', ''),
            'priority': notification_data.get('priority', 'normal'),
            'icon': self._get_icon_for_type(notification_data.get('type', 'info')),
            'auto_generated': notification_data.get('auto_generated', False),
            'action_url': notification_data.get('action_url'),
            'data': notification_data.get('data', {})
        }
        
        self.notification_queue.append(notification)
        self.notification_history.append(notification)
        
        # Garder seulement les 100 dernières notifications
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]
            
        print(f"🔔 Nouvelle notification: {notification['title']}")
        
    def _get_icon_for_type(self, notif_type):
        """Obtenir l'icône pour un type de notification"""
        icons = {
            'system': '🔧',
            'bot_status': '🤖',
            'user_action': '👤',
            'security': '🛡️',
            'error': '❌',
            'warning': '⚠️',
            'success': '✅',
            'info': 'ℹ️',
            'music': '🎵',
            'moderation': '🛡️',
            'casino': '🎰',
            'economy': '💰'
        }
        return icons.get(notif_type, 'ℹ️')
        
    def _broadcast_notification(self, notification):
        """Diffuser une notification à tous les abonnés"""
        try:
            # Ici on implémenterait l'envoi WebSocket
            # Pour l'instant, on simule
            print(f"📡 Diffusion: {notification['title']} -> {len(self.subscribers)} abonnés")
        except Exception as e:
            print(f"❌ Erreur diffusion: {e}")
            
    def get_recent_notifications(self, limit=20, user_id=None):
        """Récupérer les notifications récentes"""
        notifications = self.notification_history[-limit:]
        
        # Formater pour l'API
        formatted = []
        for notif in notifications:
            formatted.append({
                'id': notif['id'],
                'timestamp': notif['timestamp'],
                'type': notif['type'],
                'title': notif['title'],
                'message': notif['message'],
                'icon': notif['icon'],
                'priority': notif['priority'],
                'read': notif['read'],
                'time_ago': self._format_time_ago(notif['timestamp'])
            })
            
        return list(reversed(formatted))  # Plus récentes en premier
        
    def _format_time_ago(self, timestamp):
        """Formater le temps écoulé"""
        now = time.time()
        diff = int(now - timestamp)
        
        if diff < 60:
            return f"il y a {diff}s"
        elif diff < 3600:
            return f"il y a {diff // 60}m"
        elif diff < 86400:
            return f"il y a {diff // 3600}h"
        else:
            return f"il y a {diff // 86400}j"
            
    def mark_as_read(self, notification_id):
        """Marquer une notification comme lue"""
        for notif in self.notification_history:
            if notif['id'] == notification_id:
                notif['read'] = True
                return True
        return False
        
    def get_unread_count(self, user_id=None):
        """Obtenir le nombre de notifications non lues"""
        return len([n for n in self.notification_history if not n['read']])
        
    def clear_old_notifications(self, days=7):
        """Nettoyer les anciennes notifications"""
        cutoff = time.time() - (days * 24 * 3600)
        self.notification_history = [
            n for n in self.notification_history 
            if n['timestamp'] > cutoff
        ]
        
    def add_user_action_notification(self, user, action, details=None):
        """Ajouter une notification d'action utilisateur"""
        self.add_notification({
            'type': 'user_action',
            'title': f'👤 Action Utilisateur',
            'message': f'{user} a {action}',
            'priority': 'normal',
            'data': {'user': user, 'action': action, 'details': details}
        })
        
    def add_bot_event_notification(self, event, details):
        """Ajouter une notification d'événement bot"""
        self.add_notification({
            'type': 'bot_status',
            'title': f'🤖 Événement Bot',
            'message': f'{event}: {details}',
            'priority': 'normal',
            'data': {'event': event, 'details': details}
        })
        
    def add_security_alert(self, alert_type, message, priority='high'):
        """Ajouter une alerte de sécurité"""
        self.add_notification({
            'type': 'security',
            'title': f'🛡️ Alerte Sécurité',
            'message': message,
            'priority': priority,
            'data': {'alert_type': alert_type}
        })

# Instance globale
notification_system = ArsenalNotificationSystem()

# Fonctions utilitaires
def notify_user_login(username):
    """Notifier une connexion utilisateur"""
    notification_system.add_user_action_notification(
        username, 'connecté au webpanel'
    )

def notify_bot_command(command, user, guild):
    """Notifier l'exécution d'une commande bot"""
    notification_system.add_bot_event_notification(
        'Commande exécutée',
        f'{command} par {user} dans {guild}'
    )

def notify_system_status(status, details):
    """Notifier le statut système"""
    priority = 'high' if 'error' in status.lower() else 'normal'
    notification_system.add_notification({
        'type': 'system',
        'title': f'🔧 Système: {status}',
        'message': details,
        'priority': priority
    })

if __name__ == "__main__":
    # Test du système
    print("🚀 Test du système de notifications")
    
    notification_system.start()
    
    # Ajouter quelques notifications de test
    notify_user_login("XeRoX#1337")
    notify_bot_command("!play", "User#1234", "Arsenal Community")
    notify_system_status("Mise à jour", "Nouvelle version déployée")
    
    print("\n📋 Notifications récentes:")
    for notif in notification_system.get_recent_notifications(5):
        print(f"  {notif['icon']} {notif['title']} - {notif['time_ago']}")
    
    time.sleep(30)  # Laisser tourner 30 secondes
    notification_system.stop()
