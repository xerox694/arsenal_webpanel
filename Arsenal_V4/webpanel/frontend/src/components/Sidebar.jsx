import React from "react";
import { useApp } from "../contexts/AppContext";
import "./Sidebar.css";

const menuItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: '📊',
    permission: 'member'
  },
  {
    id: 'servers',
    label: 'Serveurs',
    icon: '🏠',
    permission: 'member'
  },
  {
    id: 'economy',
    label: 'Économie',
    icon: '💰',
    permission: 'member'
  },
  {
    id: 'music',
    label: 'Musique',
    icon: '🎵',
    permission: 'member'
  },
  {
    id: 'moderation',
    label: 'Modération',
    icon: '🛡️',
    permission: 'moderator'
  },
  {
    id: 'admin',
    label: 'Administration',
    icon: '⚙️',
    permission: 'admin'
  },
  {
    id: 'founder',
    label: 'Founder Panel',
    icon: '👑',
    permission: 'founder'
  },
  {
    id: 'creator',
    label: 'Creator Tools',
    icon: '🔧',
    permission: 'creator'
  }
];

export default function Sidebar() {
  const { 
    currentView, 
    navigateTo, 
    sidebarCollapsed, 
    setSidebarCollapsed,
    hasPermission,
    isAuthenticated,
    profile
  } = useApp();

  const handleNavigation = (itemId) => {
    navigateTo(itemId);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // Filtrer les éléments de menu selon les permissions
  const visibleMenuItems = menuItems.filter(item => 
    isAuthenticated && hasPermission(item.permission)
  );

  return (
    <nav className={`uix-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
      {/* Header sidebar */}
      <div className="uix-sidebar-header">
        <div className="uix-sidebar-logo">
          {!sidebarCollapsed && (
            <span className="uix-logo-text">Arsenal V4</span>
          )}
        </div>
        <button 
          className="uix-sidebar-toggle"
          onClick={toggleSidebar}
          title={sidebarCollapsed ? 'Étendre la sidebar' : 'Réduire la sidebar'}
        >
          {sidebarCollapsed ? '▶️' : '◀️'}
        </button>
      </div>

      {/* Profil utilisateur */}
      {isAuthenticated && profile && (
        <div className="uix-sidebar-profile">
          <img 
            src={profile.avatar} 
            alt="Avatar" 
            className="uix-sidebar-avatar"
          />
          {!sidebarCollapsed && (
            <div className="uix-sidebar-user-info">
              <span className="uix-username">{profile.display_name}</span>
              <span className="uix-user-role">{profile.role_display}</span>
            </div>
          )}
        </div>
      )}

      {/* Menu principal */}
      <ul className="uix-sidebar-menu">
        {isAuthenticated ? (
          visibleMenuItems.map((item) => (
            <li key={item.id} className="uix-sidebar-item">
              <button
                className={`uix-sidebar-link ${currentView === item.id ? 'active' : ''}`}
                onClick={() => handleNavigation(item.id)}
                title={sidebarCollapsed ? item.label : ''}
              >
                <span className="uix-sidebar-icon">{item.icon}</span>
                {!sidebarCollapsed && (
                  <span className="uix-sidebar-label">{item.label}</span>
                )}
              </button>
            </li>
          ))
        ) : (
          <li className="uix-sidebar-item">
            <div className="uix-sidebar-login">
              {!sidebarCollapsed && (
                <p className="uix-login-message">
                  Connectez-vous via Discord pour accéder au panel
                </p>
              )}
              <button 
                className="uix-login-btn"
                onClick={() => window.location.href = '/auth/discord'}
                title="Se connecter avec Discord"
              >
                <span className="uix-sidebar-icon">🔐</span>
                {!sidebarCollapsed && (
                  <span className="uix-sidebar-label">Se connecter</span>
                )}
              </button>
            </div>
          </li>
        )}
      </ul>

      {/* Footer sidebar */}
      <div className="uix-sidebar-footer">
        {!sidebarCollapsed && (
          <div className="uix-sidebar-version">
            <small>Arsenal V4.2.7</small>
            <small>Build: Advanced</small>
          </div>
        )}
        
        <div className="uix-sidebar-links">
          <button 
            className="uix-sidebar-link-small"
            onClick={() => navigateTo('settings')}
            title="Paramètres"
          >
            ⚙️
          </button>
          
          <button 
            className="uix-sidebar-link-small"
            onClick={() => window.open('https://github.com/xero3elite/arsenal', '_blank')}
            title="GitHub"
          >
            📚
          </button>
          
          {isAuthenticated && (
            <button 
              className="uix-sidebar-link-small"
              onClick={() => window.location.href = '/auth/logout'}
              title="Se déconnecter"
            >
              🚪
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}