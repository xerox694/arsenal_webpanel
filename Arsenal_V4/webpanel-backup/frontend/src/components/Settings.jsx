import React, { useState } from "react";
import { useApp } from "../contexts/AppContext";
import "./Settings.css";

export default function Settings() {
  const { 
    isAuthenticated, 
    profile, 
    sidebarCollapsed, 
    setSidebarCollapsed,
    addNotification 
  } = useApp();

  const [preferences, setPreferences] = useState({
    notifications: true,
    autoRefresh: true,
    compactMode: false,
    showTips: true
  });

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = () => {
    // TODO: Implémenter la sauvegarde côté serveur
    addNotification('Paramètres sauvegardés avec succès !', 'success');
  };

  if (!isAuthenticated) {
    return (
      <section className="uix-settings">
        <h3>⚙️ Paramètres</h3>
        <div className="uix-settings-message">
          <p>Connectez-vous pour accéder aux paramètres</p>
        </div>
      </section>
    );
  }

  return (
    <section className="uix-settings">
      <h3>⚙️ Paramètres du Panel</h3>
      
      {/* Informations de compte */}
      <div className="uix-settings-section">
        <h4>📱 Informations du Compte</h4>
        <div className="uix-account-info">
          <div className="uix-account-row">
            <span className="uix-label">Nom d'utilisateur :</span>
            <span className="uix-value">{profile?.display_name || 'N/A'}</span>
          </div>
          <div className="uix-account-row">
            <span className="uix-label">ID Discord :</span>
            <span className="uix-value">{profile?.id || 'N/A'}</span>
          </div>
          <div className="uix-account-row">
            <span className="uix-label">Niveau d'accès :</span>
            <span className="uix-value">{profile?.numeric_level || 'N/A'}</span>
          </div>
          <div className="uix-account-row">
            <span className="uix-label">Rôle :</span>
            <span className="uix-value">{profile?.role_display || 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Préférences d'interface */}
      <div className="uix-settings-section">
        <h4>🎨 Interface</h4>
        
        <div className="uix-settings-group">
          <label className="uix-checkbox-label">
            <input
              type="checkbox"
              checked={!sidebarCollapsed}
              onChange={(e) => setSidebarCollapsed(!e.target.checked)}
            />
            <span className="uix-checkmark"></span>
            Sidebar étendue par défaut
          </label>
        </div>

        <div className="uix-settings-group">
          <label className="uix-checkbox-label">
            <input
              type="checkbox"
              checked={preferences.compactMode}
              onChange={(e) => handlePreferenceChange('compactMode', e.target.checked)}
            />
            <span className="uix-checkmark"></span>
            Mode compact
          </label>
        </div>

        <div className="uix-settings-group">
          <label className="uix-checkbox-label">
            <input
              type="checkbox"
              checked={preferences.showTips}
              onChange={(e) => handlePreferenceChange('showTips', e.target.checked)}
            />
            <span className="uix-checkmark"></span>
            Afficher les conseils
          </label>
        </div>
      </div>

      {/* Préférences de notifications */}
      <div className="uix-settings-section">
        <h4>🔔 Notifications</h4>
        
        <div className="uix-settings-group">
          <label className="uix-checkbox-label">
            <input
              type="checkbox"
              checked={preferences.notifications}
              onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
            />
            <span className="uix-checkmark"></span>
            Notifications activées
          </label>
        </div>

        <div className="uix-settings-group">
          <label className="uix-checkbox-label">
            <input
              type="checkbox"
              checked={preferences.autoRefresh}
              onChange={(e) => handlePreferenceChange('autoRefresh', e.target.checked)}
            />
            <span className="uix-checkmark"></span>
            Actualisation automatique
          </label>
        </div>
      </div>

      {/* Actions de compte */}
      <div className="uix-settings-section">
        <h4>🔧 Actions</h4>
        
        <div className="uix-settings-actions">
          <button 
            className="uix-neon-btn"
            onClick={saveSettings}
          >
            💾 Sauvegarder les paramètres
          </button>
          
          <button 
            className="uix-neon-btn secondary"
            onClick={() => window.location.reload()}
          >
            🔄 Actualiser la page
          </button>
          
          <button 
            className="uix-neon-btn danger"
            onClick={() => window.location.href = '/auth/logout'}
          >
            🚪 Se déconnecter
          </button>
        </div>
      </div>

      {/* Informations système */}
      <div className="uix-settings-section">
        <h4>ℹ️ Informations Système</h4>
        <div className="uix-system-info">
          <div className="uix-info-row">
            <span className="uix-label">Version Panel :</span>
            <span className="uix-value">Arsenal V4.2.7</span>
          </div>
          <div className="uix-info-row">
            <span className="uix-label">Build :</span>
            <span className="uix-value">Advanced Edition</span>
          </div>
          <div className="uix-info-row">
            <span className="uix-label">Dernière mise à jour :</span>
            <span className="uix-value">{new Date().toLocaleDateString('fr-FR')}</span>
          </div>
        </div>
      </div>
    </section>
  );
}