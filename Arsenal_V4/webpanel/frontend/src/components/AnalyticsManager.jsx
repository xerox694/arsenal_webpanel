import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAPI, apiPost } from '../hooks/useAPI';
import './AnalyticsManager.css';

const AnalyticsManager = () => {
  console.log('📊 Phase 6: Initialisation AnalyticsManager');
  
  const { 
    isAuthenticated, 
    hasPermission, 
    selectedServer, 
    addNotification,
    profile 
  } = useApp();

  // États locaux
  const [activeTab, setActiveTab] = useState('overview');
  const [serverMetrics, setServerMetrics] = useState([]);
  const [userMetrics, setUserMetrics] = useState([]);
  const [events, setEvents] = useState([]);
  const [analyticsConfig, setAnalyticsConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log('📊 Phase 6: États initialisés', {
    activeTab,
    hasAnalyticsAccess: hasPermission('admin'),
    selectedServer: selectedServer?.id
  });

  // Hooks pour les données analytics
  const { data: metricsData, loading: metricsLoading } = useAPI(
    selectedServer ? `/analytics/metrics/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: usersData, loading: usersLoading } = useAPI(
    selectedServer ? `/analytics/users/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: eventsData, loading: eventsLoading } = useAPI(
    selectedServer ? `/analytics/events/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: configData, loading: configLoading } = useAPI(
    selectedServer ? `/analytics/config/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  useEffect(() => {
    console.log('🔄 Phase 6: Mise à jour des données', {
      metricsData,
      usersData,
      eventsData,
      configData,
      loading: metricsLoading || usersLoading || eventsLoading || configLoading
    });

    if (metricsData) {
      setServerMetrics(metricsData.metrics || []);
      console.log('✅ Phase 6: Métriques serveur chargées', metricsData);
    }

    if (usersData) {
      setUserMetrics(usersData.users || []);
      console.log('✅ Phase 6: Métriques utilisateur chargées', usersData);
    }

    if (eventsData) {
      setEvents(eventsData.events || []);
      console.log('✅ Phase 6: Événements chargés', eventsData);
    }

    if (configData) {
      setAnalyticsConfig(configData.config || {});
      console.log('✅ Phase 6: Configuration analytics chargée', configData);
    }

    const isLoading = metricsLoading || usersLoading || eventsLoading || configLoading;
    setLoading(isLoading);
    
    if (!isLoading) {
      console.log('🎉 Phase 6: Toutes les données chargées !');
    }
  }, [metricsData, usersData, eventsData, configData, metricsLoading, usersLoading, eventsLoading, configLoading]);

  // Gestion des onglets
  const handleTabChange = (tab) => {
    console.log(`🔄 Phase 6: Changement d'onglet: ${activeTab} -> ${tab}`);
    setActiveTab(tab);
  };

  // Génération de rapport (Admin+)
  const generateReport = async (type, period = 'week') => {
    console.log('📋 Phase 6: Génération rapport', { type, period });
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 6: Permissions insuffisantes pour générer rapport');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/analytics/report/${selectedServer.id}`, {
        type,
        period,
        generated_by: profile?.id
      });
      
      console.log('✅ Phase 6: Rapport généré avec succès', result);
      addNotification('Rapport généré avec succès !', 'success');
      
      // Télécharger le rapport si disponible
      if (result.download_url) {
        window.open(result.download_url, '_blank');
      }
    } catch (error) {
      console.error('❌ Phase 6: Erreur lors de la génération', error);
      addNotification('Erreur lors de la génération du rapport', 'error');
    }
  };

  // Sauvegarde configuration (Admin+)
  const saveAnalyticsConfig = async (newConfig) => {
    console.log('💾 Phase 6: Tentative de sauvegarde config analytics', newConfig);
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 6: Permissions insuffisantes pour modifier la config');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/analytics/config/${selectedServer.id}`, newConfig);
      console.log('✅ Phase 6: Configuration sauvegardée avec succès', result);
      setAnalyticsConfig({ ...analyticsConfig, ...newConfig });
      addNotification('Configuration analytics mise à jour !', 'success');
    } catch (error) {
      console.error('❌ Phase 6: Erreur lors de la sauvegarde', error);
      addNotification('Erreur lors de la sauvegarde', 'error');
    }
  };

  // Interface de chargement
  if (loading) {
    console.log('⏳ Phase 6: Affichage du loader');
    return (
      <div className="analytics-manager">
        <div className="analytics-header">
          <h2>📊 Système Analytics</h2>
          <p>Phase 6 - Analytics Manager Avancé</p>
        </div>
        <div className="analytics-loading">
          <div className="analytics-spinner"></div>
          <p>Chargement des données analytics...</p>
        </div>
      </div>
    );
  }

  // Vérification d'authentification
  if (!isAuthenticated) {
    console.log('🔐 Phase 6: Utilisateur non connecté');
    return (
      <div className="analytics-manager">
        <div className="analytics-header">
          <h2>📊 Système Analytics</h2>
        </div>
        <div className="analytics-auth-required">
          <h3>🔐 Connexion Requise</h3>
          <p>Connectez-vous pour accéder au système analytics</p>
          <button 
            className="analytics-btn-primary"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </div>
    );
  }

  // Vérification des permissions
  if (!hasPermission('admin')) {
    console.log('🔐 Phase 6: Permissions insuffisantes');
    return (
      <div className="analytics-manager">
        <div className="analytics-header">
          <h2>📊 Système Analytics</h2>
        </div>
        <div className="analytics-permissions-required">
          <h3>🔒 Permissions Insuffisantes</h3>
          <p>Vous devez être administrateur ou plus pour accéder aux analytics</p>
          <div className="analytics-required-permissions">
            <span className="analytics-permission-badge">Administrateur</span>
            <span className="analytics-permission-badge">Founder</span>
            <span className="analytics-permission-badge">Creator</span>
          </div>
        </div>
      </div>
    );
  }

  console.log('🎨 Phase 6: Rendu de l\'interface principale');

  return (
    <div className="analytics-manager">
      {/* Header */}
      <div className="analytics-header">
        <h2>📊 Système Analytics Arsenal V4</h2>
        <p>Phase 6 - Analytics Manager Complet</p>
        {selectedServer && (
          <div className="analytics-server-info">
            <span>Serveur: {selectedServer.name}</span>
            <span className="analytics-server-badge">
              {hasPermission('founder') ? 'Founder' : hasPermission('admin') ? 'Admin' : 'Membre'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation des onglets */}
      <div className="analytics-tabs">
        <button 
          className={`analytics-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          📊 Vue d'ensemble
        </button>
        <button 
          className={`analytics-tab ${activeTab === 'server' ? 'active' : ''}`}
          onClick={() => handleTabChange('server')}
        >
          🏠 Serveur
        </button>
        <button 
          className={`analytics-tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => handleTabChange('users')}
        >
          👥 Utilisateurs
        </button>
        <button 
          className={`analytics-tab ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => handleTabChange('events')}
        >
          📅 Événements
        </button>
        <button 
          className={`analytics-tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => handleTabChange('reports')}
        >
          📋 Rapports
        </button>
        <button 
          className={`analytics-tab ${activeTab === 'config' ? 'active' : ''}`}
          onClick={() => handleTabChange('config')}
        >
          ⚙️ Configuration
        </button>
      </div>

      {/* Contenu des onglets */}
      <div className="analytics-content">
        {activeTab === 'overview' && (
          <AnalyticsOverview 
            serverMetrics={serverMetrics}
            userMetrics={userMetrics}
            events={events}
          />
        )}
        
        {activeTab === 'server' && (
          <AnalyticsServer 
            metrics={serverMetrics}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'users' && (
          <AnalyticsUsers 
            users={userMetrics}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'events' && (
          <AnalyticsEvents 
            events={events}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'reports' && (
          <AnalyticsReports 
            onGenerateReport={generateReport}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'config' && (
          <AnalyticsConfig 
            config={analyticsConfig}
            onSave={saveAnalyticsConfig}
          />
        )}
      </div>
    </div>
  );
};

// Composant Vue d'ensemble
const AnalyticsOverview = ({ serverMetrics, userMetrics, events }) => {
  console.log('📊 Phase 6: Rendu AnalyticsOverview', { serverMetrics, userMetrics, events });

  // Calculs de statistiques
  const totalMessages = serverMetrics.reduce((sum, metric) => sum + metric.messages_count, 0);
  const totalMembers = serverMetrics.length > 0 ? serverMetrics[serverMetrics.length - 1].member_count : 0;
  const totalVoiceMinutes = serverMetrics.reduce((sum, metric) => sum + metric.voice_minutes, 0);
  const totalCommands = serverMetrics.reduce((sum, metric) => sum + metric.commands_used, 0);

  const activeUsers = userMetrics.filter(user => 
    user.messages_sent > 0 || user.voice_minutes > 0 || user.commands_used > 0
  ).length;

  return (
    <div className="analytics-overview">
      {/* Statistiques principales */}
      <div className="analytics-main-stats">
        <div className="analytics-stat-card">
          <div className="analytics-stat-icon">👥</div>
          <div className="analytics-stat-content">
            <span className="analytics-stat-value">{totalMembers.toLocaleString()}</span>
            <span className="analytics-stat-label">Membres totaux</span>
          </div>
        </div>
        
        <div className="analytics-stat-card">
          <div className="analytics-stat-icon">💬</div>
          <div className="analytics-stat-content">
            <span className="analytics-stat-value">{totalMessages.toLocaleString()}</span>
            <span className="analytics-stat-label">Messages envoyés</span>
          </div>
        </div>
        
        <div className="analytics-stat-card">
          <div className="analytics-stat-icon">🎤</div>
          <div className="analytics-stat-content">
            <span className="analytics-stat-value">{Math.floor(totalVoiceMinutes / 60).toLocaleString()}h</span>
            <span className="analytics-stat-label">Temps vocal</span>
          </div>
        </div>
        
        <div className="analytics-stat-card">
          <div className="analytics-stat-icon">⚡</div>
          <div className="analytics-stat-content">
            <span className="analytics-stat-value">{totalCommands.toLocaleString()}</span>
            <span className="analytics-stat-label">Commandes utilisées</span>
          </div>
        </div>
        
        <div className="analytics-stat-card">
          <div className="analytics-stat-icon">🔥</div>
          <div className="analytics-stat-content">
            <span className="analytics-stat-value">{activeUsers}</span>
            <span className="analytics-stat-label">Utilisateurs actifs</span>
          </div>
        </div>
      </div>

      {/* Graphiques de tendances */}
      <div className="analytics-charts-section">
        <div className="analytics-chart-card">
          <h3>📈 Évolution des messages (7 derniers jours)</h3>
          <div className="analytics-chart-placeholder">
            {serverMetrics.length > 0 ? (
              <div className="analytics-simple-chart">
                {serverMetrics.slice(-7).map((metric, index) => (
                  <div key={index} className="analytics-chart-bar">
                    <div 
                      className="analytics-chart-bar-fill"
                      style={{ 
                        height: `${Math.min(100, (metric.messages_count / Math.max(...serverMetrics.map(m => m.messages_count))) * 100)}%` 
                      }}
                    ></div>
                    <span className="analytics-chart-label">
                      {new Date(metric.date).toLocaleDateString('fr-FR', { weekday: 'short' })}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p>Aucune donnée disponible</p>
            )}
          </div>
        </div>

        <div className="analytics-chart-card">
          <h3>🎤 Activité vocale (7 derniers jours)</h3>
          <div className="analytics-chart-placeholder">
            {serverMetrics.length > 0 ? (
              <div className="analytics-simple-chart">
                {serverMetrics.slice(-7).map((metric, index) => (
                  <div key={index} className="analytics-chart-bar">
                    <div 
                      className="analytics-chart-bar-fill voice"
                      style={{ 
                        height: `${Math.min(100, (metric.voice_minutes / Math.max(...serverMetrics.map(m => m.voice_minutes))) * 100)}%` 
                      }}
                    ></div>
                    <span className="analytics-chart-label">
                      {new Date(metric.date).toLocaleDateString('fr-FR', { weekday: 'short' })}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p>Aucune donnée disponible</p>
            )}
          </div>
        </div>
      </div>

      {/* Top utilisateurs */}
      <div className="analytics-top-users">
        <h3>🏆 Top Utilisateurs Actifs</h3>
        {userMetrics.length > 0 ? (
          <div className="analytics-users-list">
            {userMetrics
              .sort((a, b) => (b.messages_sent + b.commands_used) - (a.messages_sent + a.commands_used))
              .slice(0, 10)
              .map((user, index) => (
                <div key={user.user_id} className="analytics-user-item">
                  <span className="analytics-user-rank">#{index + 1}</span>
                  <span className="analytics-user-name">
                    {user.username || `User_${user.user_id?.slice(-4)}`}
                  </span>
                  <div className="analytics-user-stats">
                    <span>💬 {user.messages_sent}</span>
                    <span>⚡ {user.commands_used}</span>
                    <span>🎤 {Math.floor(user.voice_minutes)}min</span>
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <p>Aucune donnée utilisateur disponible</p>
        )}
      </div>

      {/* Événements récents */}
      <div className="analytics-recent-events">
        <h3>📅 Événements Récents</h3>
        {events.length > 0 ? (
          <div className="analytics-events-list">
            {events.slice(0, 5).map((event, index) => (
              <div key={event.id || index} className="analytics-event-item">
                <span className="analytics-event-type">{event.event_type}</span>
                <span className="analytics-event-time">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
                <span className="analytics-event-data">
                  {event.event_data || 'Aucun détail'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p>Aucun événement récent</p>
        )}
      </div>
    </div>
  );
};

// Placeholders pour les autres composants (à implémenter)
const AnalyticsServer = ({ metrics, serverId }) => (
  <div className="analytics-server">
    <h3>🏠 Métriques Serveur Détaillées</h3>
    <div className="analytics-coming-soon">
      <p>🚧 Interface serveur en développement</p>
      <p>Cette section affichera :</p>
      <ul>
        <li>📊 Graphiques détaillés d'activité</li>
        <li>📈 Tendances à long terme</li>
        <li>📋 Comparaisons temporelles</li>
        <li>📊 Statistiques par canal</li>
      </ul>
    </div>
  </div>
);

const AnalyticsUsers = ({ users, serverId }) => (
  <div className="analytics-users">
    <h3>👥 Analyse Utilisateurs</h3>
    <div className="analytics-coming-soon">
      <p>🚧 Interface utilisateurs en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>📊 Profils utilisateurs détaillés</li>
        <li>📈 Évolution de l'activité</li>
        <li>🏆 Classements personnalisés</li>
        <li>📋 Rapports individuels</li>
      </ul>
    </div>
  </div>
);

const AnalyticsEvents = ({ events, serverId }) => (
  <div className="analytics-events">
    <h3>📅 Journal des Événements</h3>
    <div className="analytics-coming-soon">
      <p>🚧 Interface événements en développement</p>
      <p>Cette section affichera :</p>
      <ul>
        <li>📅 Chronologie complète</li>
        <li>🔍 Filtres avancés</li>
        <li>📊 Analyse des patterns</li>
        <li>📤 Export des données</li>
      </ul>
    </div>
  </div>
);

const AnalyticsReports = ({ onGenerateReport, serverId }) => (
  <div className="analytics-reports">
    <h3>📋 Génération de Rapports</h3>
    <div className="analytics-coming-soon">
      <p>🚧 Interface rapports en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>📋 Rapports automatisés</li>
        <li>📊 Formats personnalisables</li>
        <li>📤 Export PDF/Excel</li>
        <li>📧 Envoi automatique</li>
      </ul>
    </div>
  </div>
);

const AnalyticsConfig = ({ config, onSave }) => (
  <div className="analytics-config">
    <h3>⚙️ Configuration Analytics</h3>
    <div className="analytics-coming-soon">
      <p>🚧 Interface configuration en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⚙️ Paramètres de collecte</li>
        <li>📊 Métriques personnalisées</li>
        <li>🔄 Fréquence de mise à jour</li>
        <li>🔒 Paramètres de confidentialité</li>
      </ul>
    </div>
  </div>
);

export default AnalyticsManager;
