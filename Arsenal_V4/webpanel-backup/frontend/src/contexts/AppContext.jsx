import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth, useStats, useUserProfile, useUserPermissions } from '../hooks/useAPI';

// Context pour l'état global de l'application
const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  // États locaux
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedServer, setSelectedServer] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Hooks API
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const { stats, loading: statsLoading } = useStats();
  const { profile, loading: profileLoading } = useUserProfile();
  const { permissions, loading: permissionsLoading } = useUserPermissions();

  // Fonction pour ajouter une notification
  const addNotification = (message, type = 'info', duration = 5000) => {
    const id = Date.now();
    const notification = { id, message, type, timestamp: new Date() };
    
    setNotifications(prev => [...prev, notification]);
    
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  };

  // Fonction pour supprimer une notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  // Fonctions utilitaires pour les permissions
  const hasPermission = (level) => {
    if (!permissions) return false;
    const userLevel = permissions.numeric_level || 0;
    const requiredLevels = {
      creator: 1000,
      founder: 800,
      admin: 600,
      moderator: 400,
      member: 200
    };
    return userLevel >= (requiredLevels[level] || 0);
  };

  const isCreator = () => hasPermission('creator');
  const isFounder = () => hasPermission('founder');
  const isAdmin = () => hasPermission('admin');
  const isModerator = () => hasPermission('moderator');

  // Navigation functions
  const navigateTo = (view, serverContext = null) => {
    setCurrentView(view);
    if (serverContext) {
      setSelectedServer(serverContext);
    }
  };

  // Fonction pour obtenir les badges utilisateur
  const getUserBadges = () => {
    if (!permissions) return [];
    
    const badges = [];
    
    if (isCreator()) {
      badges.push({
        name: 'Bot Creator',
        icon: '🔧',
        color: '#ff6b6b',
        priority: 1000
      });
    }
    
    if (isFounder()) {
      badges.push({
        name: 'Server Founder',
        icon: '👑',
        color: '#ffd93d',
        priority: 800
      });
    }
    
    if (isAdmin()) {
      badges.push({
        name: 'Administrator',
        icon: '⚡',
        color: '#74c0fc',
        priority: 600
      });
    }
    
    if (isModerator()) {
      badges.push({
        name: 'Moderator',
        icon: '🛡️',
        color: '#51cf66',
        priority: 400
      });
    }

    // Badges spéciaux basés sur les données utilisateur
    if (profile?.created_at) {
      const joinDate = new Date(profile.created_at);
      const monthsAgo = (Date.now() - joinDate.getTime()) / (1000 * 60 * 60 * 24 * 30);
      
      if (monthsAgo >= 12) {
        badges.push({
          name: 'Veteran User',
          icon: '🏆',
          color: '#e599f7',
          priority: 300
        });
      } else if (monthsAgo >= 6) {
        badges.push({
          name: 'Experienced User',
          icon: '⭐',
          color: '#91a7ff',
          priority: 250
        });
      }
    }

    return badges.sort((a, b) => b.priority - a.priority);
  };

  // État de chargement global
  const isLoading = authLoading || statsLoading || profileLoading || permissionsLoading;

  const value = {
    // États de base
    currentView,
    selectedServer,
    sidebarCollapsed,
    notifications,
    isLoading,

    // Données API
    user,
    isAuthenticated,
    stats,
    profile,
    permissions,

    // Actions
    setCurrentView,
    setSelectedServer,
    setSidebarCollapsed,
    addNotification,
    removeNotification,
    navigateTo,

    // Utilitaires permissions
    hasPermission,
    isCreator,
    isFounder,
    isAdmin,
    isModerator,
    getUserBadges
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
