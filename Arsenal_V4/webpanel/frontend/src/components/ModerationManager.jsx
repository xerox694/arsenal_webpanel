import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAPI, apiPost, apiDelete } from '../hooks/useAPI';
import './ModerationManager.css';

const ModerationManager = () => {
  console.log('🛡️ Phase 3: Initialisation ModerationManager');
  
  const { 
    isAuthenticated, 
    hasPermission, 
    selectedServer, 
    addNotification,
    profile 
  } = useApp();

  // États locaux
  const [activeTab, setActiveTab] = useState('overview');
  const [moderationLogs, setModerationLogs] = useState([]);
  const [activeWarnings, setActiveWarnings] = useState([]);
  const [moderationConfig, setModerationConfig] = useState(null);
  const [automodConfig, setAutomodConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log('📊 Phase 3: États initialisés', {
    activeTab,
    hasModerationAccess: hasPermission('moderator'),
    isAdmin: hasPermission('admin'),
    selectedServer: selectedServer?.id
  });

  // Hooks pour les données de modération
  const { data: moderationData, loading: moderationLoading } = useAPI(
    selectedServer ? `/moderation/logs/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: warningsData, loading: warningsLoading } = useAPI(
    selectedServer ? `/moderation/warnings/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: configData, loading: configLoading } = useAPI(
    selectedServer ? `/moderation/config/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  useEffect(() => {
    console.log('🔄 Phase 3: Mise à jour des données', {
      moderationData,
      warningsData,
      configData,
      loading: moderationLoading || warningsLoading || configLoading
    });

    if (moderationData) {
      setModerationLogs(moderationData.logs || []);
      console.log('✅ Phase 3: Logs de modération chargés', moderationData);
    }

    if (warningsData) {
      setActiveWarnings(warningsData.warnings || []);
      console.log('✅ Phase 3: Avertissements chargés', warningsData);
    }

    if (configData) {
      setModerationConfig(configData.moderation || {});
      setAutomodConfig(configData.automod || {});
      console.log('✅ Phase 3: Configuration modération chargée', configData);
    }

    const isLoading = moderationLoading || warningsLoading || configLoading;
    setLoading(isLoading);
    
    if (!isLoading) {
      console.log('🎉 Phase 3: Toutes les données chargées !');
    }
  }, [moderationData, warningsData, configData, moderationLoading, warningsLoading, configLoading]);

  // Gestion des onglets
  const handleTabChange = (tab) => {
    console.log(`🔄 Phase 3: Changement d'onglet: ${activeTab} -> ${tab}`);
    setActiveTab(tab);
  };

  // Sauvegarde de configuration (Admin+)
  const saveModerationConfig = async (newConfig) => {
    console.log('💾 Phase 3: Tentative de sauvegarde config modération', newConfig);
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 3: Permissions insuffisantes pour modifier la config');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    if (!selectedServer) {
      console.error('❌ Phase 3: Aucun serveur sélectionné');
      addNotification('Veuillez sélectionner un serveur', 'error');
      return;
    }

    try {
      console.log('🚀 Phase 3: Envoi de la configuration au serveur');
      const result = await apiPost(`/moderation/config/${selectedServer.id}`, newConfig);
      
      console.log('✅ Phase 3: Configuration sauvegardée avec succès', result);
      setModerationConfig({ ...moderationConfig, ...newConfig.moderation });
      setAutomodConfig({ ...automodConfig, ...newConfig.automod });
      addNotification('Configuration de modération mise à jour !', 'success');
    } catch (error) {
      console.error('❌ Phase 3: Erreur lors de la sauvegarde', error);
      addNotification('Erreur lors de la sauvegarde', 'error');
    }
  };

  // Action de modération
  const executeModAction = async (action, userId, reason, duration = null) => {
    console.log('⚡ Phase 3: Exécution action modération', { action, userId, reason, duration });
    
    if (!hasPermission('moderator')) {
      console.error('❌ Phase 3: Permissions insuffisantes pour modérer');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const payload = {
        action,
        user_id: userId,
        reason,
        duration,
        moderator_id: profile.id
      };

      console.log('🚀 Phase 3: Envoi action modération', payload);
      const result = await apiPost(`/moderation/action/${selectedServer.id}`, payload);
      
      console.log('✅ Phase 3: Action exécutée avec succès', result);
      addNotification(`Action ${action} exécutée avec succès`, 'success');
      
      // Recharger les données
      window.location.reload();
    } catch (error) {
      console.error('❌ Phase 3: Erreur lors de l\'action', error);
      addNotification(`Erreur lors de l'action ${action}`, 'error');
    }
  };

  // Interface de chargement
  if (loading) {
    console.log('⏳ Phase 3: Affichage du loader');
    return (
      <div className="moderation-manager">
        <div className="moderation-header">
          <h2>🛡️ Système de Modération</h2>
          <p>Phase 3 - Moderation Manager Avancé</p>
        </div>
        <div className="moderation-loading">
          <div className="moderation-spinner"></div>
          <p>Chargement des données de modération...</p>
        </div>
      </div>
    );
  }

  // Vérification d'authentification
  if (!isAuthenticated) {
    console.log('🔐 Phase 3: Utilisateur non connecté');
    return (
      <div className="moderation-manager">
        <div className="moderation-header">
          <h2>🛡️ Système de Modération</h2>
        </div>
        <div className="moderation-auth-required">
          <h3>🔐 Connexion Requise</h3>
          <p>Connectez-vous pour accéder au système de modération</p>
          <button 
            className="moderation-btn-primary"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </div>
    );
  }

  // Vérification des permissions
  if (!hasPermission('moderator')) {
    console.log('🔐 Phase 3: Permissions insuffisantes');
    return (
      <div className="moderation-manager">
        <div className="moderation-header">
          <h2>🛡️ Système de Modération</h2>
        </div>
        <div className="moderation-permissions-required">
          <h3>🔒 Permissions Insuffisantes</h3>
          <p>Vous devez être modérateur ou plus pour accéder à cette section</p>
          <div className="moderation-required-permissions">
            <span className="moderation-permission-badge">Modérateur</span>
            <span className="moderation-permission-badge">Administrateur</span>
            <span className="moderation-permission-badge">Founder</span>
          </div>
        </div>
      </div>
    );
  }

  console.log('🎨 Phase 3: Rendu de l\'interface principale');

  return (
    <div className="moderation-manager">
      {/* Header */}
      <div className="moderation-header">
        <h2>🛡️ Système de Modération Arsenal V4</h2>
        <p>Phase 3 - Moderation Manager Complet</p>
        {selectedServer && (
          <div className="moderation-server-info">
            <span>Serveur: {selectedServer.name}</span>
            <span className="moderation-server-badge">
              {hasPermission('founder') ? 'Founder' : hasPermission('admin') ? 'Admin' : 'Modérateur'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation des onglets */}
      <div className="moderation-tabs">
        <button 
          className={`moderation-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          📊 Vue d'ensemble
        </button>
        <button 
          className={`moderation-tab ${activeTab === 'actions' ? 'active' : ''}`}
          onClick={() => handleTabChange('actions')}
        >
          ⚡ Actions
        </button>
        <button 
          className={`moderation-tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => handleTabChange('logs')}
        >
          📋 Historique
        </button>
        <button 
          className={`moderation-tab ${activeTab === 'warnings' ? 'active' : ''}`}
          onClick={() => handleTabChange('warnings')}
        >
          ⚠️ Avertissements
        </button>
        {hasPermission('admin') && (
          <>
            <button 
              className={`moderation-tab ${activeTab === 'automod' ? 'active' : ''}`}
              onClick={() => handleTabChange('automod')}
            >
              🤖 AutoMod
            </button>
            <button 
              className={`moderation-tab ${activeTab === 'config' ? 'active' : ''}`}
              onClick={() => handleTabChange('config')}
            >
              ⚙️ Configuration
            </button>
          </>
        )}
      </div>

      {/* Contenu des onglets */}
      <div className="moderation-content">
        {activeTab === 'overview' && (
          <ModerationOverview 
            logs={moderationLogs}
            warnings={activeWarnings}
            config={moderationConfig}
          />
        )}
        
        {activeTab === 'actions' && (
          <ModerationActions 
            onExecuteAction={executeModAction}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'logs' && (
          <ModerationLogs 
            logs={moderationLogs}
          />
        )}
        
        {activeTab === 'warnings' && (
          <ModerationWarnings 
            warnings={activeWarnings}
            onExecuteAction={executeModAction}
          />
        )}
        
        {activeTab === 'automod' && hasPermission('admin') && (
          <AutoModeration 
            config={automodConfig}
            onSave={(config) => saveModerationConfig({ automod: config })}
          />
        )}
        
        {activeTab === 'config' && hasPermission('admin') && (
          <ModerationConfig 
            config={moderationConfig}
            onSave={(config) => saveModerationConfig({ moderation: config })}
          />
        )}
      </div>
    </div>
  );
};

// Composant Vue d'ensemble
const ModerationOverview = ({ logs, warnings, config }) => {
  console.log('📊 Phase 3: Rendu ModerationOverview', { logs, warnings, config });
  
  // Statistiques sur les 7 derniers jours
  const getRecentStats = () => {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recentLogs = logs.filter(log => new Date(log.timestamp) > sevenDaysAgo);
    
    return {
      total_actions: recentLogs.length,
      warns: recentLogs.filter(log => log.action === 'warn').length,
      mutes: recentLogs.filter(log => log.action === 'mute').length,
      kicks: recentLogs.filter(log => log.action === 'kick').length,
      bans: recentLogs.filter(log => log.action === 'ban').length
    };
  };

  const stats = getRecentStats();

  return (
    <div className="moderation-overview">
      <div className="moderation-grid">
        {/* Statistiques récentes */}
        <div className="moderation-card">
          <h3>📊 Activité (7 derniers jours)</h3>
          <div className="moderation-stats">
            <div className="moderation-stat">
              <span className="moderation-stat-icon">⚡</span>
              <div className="moderation-stat-info">
                <span className="moderation-stat-value">{stats.total_actions}</span>
                <span className="moderation-stat-label">Actions totales</span>
              </div>
            </div>
            <div className="moderation-stat">
              <span className="moderation-stat-icon">⚠️</span>
              <div className="moderation-stat-info">
                <span className="moderation-stat-value">{stats.warns}</span>
                <span className="moderation-stat-label">Avertissements</span>
              </div>
            </div>
            <div className="moderation-stat">
              <span className="moderation-stat-icon">🔇</span>
              <div className="moderation-stat-info">
                <span className="moderation-stat-value">{stats.mutes}</span>
                <span className="moderation-stat-label">Mutes</span>
              </div>
            </div>
            <div className="moderation-stat">
              <span className="moderation-stat-icon">👢</span>
              <div className="moderation-stat-info">
                <span className="moderation-stat-value">{stats.kicks}</span>
                <span className="moderation-stat-label">Expulsions</span>
              </div>
            </div>
            <div className="moderation-stat">
              <span className="moderation-stat-icon">🔨</span>
              <div className="moderation-stat-info">
                <span className="moderation-stat-value">{stats.bans}</span>
                <span className="moderation-stat-label">Bannissements</span>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration actuelle */}
        <div className="moderation-card">
          <h3>⚙️ Configuration Actuelle</h3>
          <div className="moderation-config-summary">
            <div className="moderation-config-item">
              <span className="moderation-config-label">Auto-modération :</span>
              <span className={`moderation-config-value ${config?.automod_enabled ? 'enabled' : 'disabled'}`}>
                {config?.automod_enabled ? '✅ Activée' : '❌ Désactivée'}
              </span>
            </div>
            <div className="moderation-config-item">
              <span className="moderation-config-label">Logs activés :</span>
              <span className={`moderation-config-value ${config?.logging_enabled ? 'enabled' : 'disabled'}`}>
                {config?.logging_enabled ? '✅ Oui' : '❌ Non'}
              </span>
            </div>
            <div className="moderation-config-item">
              <span className="moderation-config-label">Seuil auto-ban :</span>
              <span className="moderation-config-value">
                {config?.auto_ban_threshold || 5} avertissements
              </span>
            </div>
            <div className="moderation-config-item">
              <span className="moderation-config-label">Filtre de mots :</span>
              <span className={`moderation-config-value ${config?.word_filter_enabled ? 'enabled' : 'disabled'}`}>
                {config?.word_filter_enabled ? '✅ Activé' : '❌ Désactivé'}
              </span>
            </div>
          </div>
        </div>

        {/* Avertissements actifs */}
        <div className="moderation-card">
          <h3>⚠️ Avertissements Actifs</h3>
          {warnings.length > 0 ? (
            <div className="moderation-warnings-summary">
              {warnings.slice(0, 5).map((warning, index) => (
                <div key={warning.id || index} className="moderation-warning-item">
                  <span className="moderation-warning-user">
                    {warning.username || `User_${warning.user_id?.slice(-4)}`}
                  </span>
                  <span className="moderation-warning-count">
                    {warning.warning_count} warn{warning.warning_count > 1 ? 's' : ''}
                  </span>
                  <span className="moderation-warning-last">
                    {warning.last_warning ? new Date(warning.last_warning).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              ))}
              {warnings.length > 5 && (
                <div className="moderation-warnings-more">
                  +{warnings.length - 5} autre{warnings.length - 5 > 1 ? 's' : ''} utilisateur{warnings.length - 5 > 1 ? 's' : ''}
                </div>
              )}
            </div>
          ) : (
            <div className="moderation-no-warnings">
              <p>🎉 Aucun avertissement actif</p>
              <p>Votre serveur est bien modéré !</p>
            </div>
          )}
        </div>

        {/* Actions récentes */}
        <div className="moderation-card">
          <h3>📋 Actions Récentes</h3>
          {logs.length > 0 ? (
            <div className="moderation-recent-logs">
              {logs.slice(0, 5).map((log, index) => (
                <div key={log.id || index} className="moderation-log-item">
                  <span className={`moderation-action-badge ${log.action}`}>
                    {log.action?.toUpperCase()}
                  </span>
                  <div className="moderation-log-details">
                    <span className="moderation-log-target">
                      {log.target_username || `User_${log.target_user_id?.slice(-4)}`}
                    </span>
                    <span className="moderation-log-reason">
                      {log.reason || 'Aucune raison spécifiée'}
                    </span>
                    <span className="moderation-log-time">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="moderation-no-logs">
              <p>📋 Aucune action récente</p>
              <p>Les actions de modération apparaîtront ici</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Placeholder pour les autres composants (à implémenter)
const ModerationActions = ({ onExecuteAction, serverId }) => (
  <div className="moderation-actions">
    <h3>⚡ Actions de Modération</h3>
    <div className="moderation-coming-soon">
      <p>🚧 Interface d'actions en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⚠️ Avertir un utilisateur</li>
        <li>🔇 Muter temporairement</li>
        <li>👢 Expulser du serveur</li>
        <li>🔨 Bannir définitivement</li>
        <li>🔓 Lever des sanctions</li>
      </ul>
    </div>
  </div>
);

const ModerationLogs = ({ logs }) => (
  <div className="moderation-logs">
    <h3>📋 Historique de Modération</h3>
    <div className="moderation-coming-soon">
      <p>🚧 Interface d'historique en développement</p>
      <p>Cette section affichera :</p>
      <ul>
        <li>📊 Toutes les actions de modération</li>
        <li>🔍 Filtres par type, utilisateur, modérateur</li>
        <li>📈 Graphiques d'activité</li>
        <li>📤 Export des logs</li>
      </ul>
    </div>
  </div>
);

const ModerationWarnings = ({ warnings, onExecuteAction }) => (
  <div className="moderation-warnings">
    <h3>⚠️ Gestion des Avertissements</h3>
    <div className="moderation-coming-soon">
      <p>🚧 Interface d'avertissements en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>📊 Liste détaillée des avertissements</li>
        <li>🔍 Recherche par utilisateur</li>
        <li>🗑️ Suppression d'avertissements</li>
        <li>⚡ Actions rapides basées sur les seuils</li>
      </ul>
    </div>
  </div>
);

const AutoModeration = ({ config, onSave }) => (
  <div className="auto-moderation">
    <h3>🤖 Configuration Auto-Modération</h3>
    <div className="moderation-coming-soon">
      <p>🚧 Interface d'auto-modération en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>🔧 Configurer les filtres automatiques</li>
        <li>📝 Gestion des mots interdits</li>
        <li>⚡ Actions automatiques</li>
        <li>🎯 Seuils de déclenchement</li>
      </ul>
    </div>
  </div>
);

const ModerationConfig = ({ config, onSave }) => (
  <div className="moderation-config">
    <h3>⚙️ Configuration Générale</h3>
    <div className="moderation-coming-soon">
      <p>🚧 Interface de configuration en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⚙️ Paramètres généraux de modération</li>
        <li>📊 Configuration des logs</li>
        <li>🔧 Personnalisation des sanctions</li>
        <li>👥 Gestion des rôles de modération</li>
      </ul>
    </div>
  </div>
);

export default ModerationManager;
