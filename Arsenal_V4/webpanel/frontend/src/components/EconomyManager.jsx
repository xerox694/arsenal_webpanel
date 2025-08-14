import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAPI, apiPost } from '../hooks/useAPI';
import './EconomyManager.css';

const EconomyManager = () => {
  console.log('🏗️ Phase 2: Initialisation EconomyManager');
  
  const { 
    isAuthenticated, 
    hasPermission, 
    selectedServer, 
    addNotification,
    profile 
  } = useApp();

  // États locaux
  const [activeTab, setActiveTab] = useState('overview');
  const [economyConfig, setEconomyConfig] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [leaderboards, setLeaderboards] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  console.log('📊 Phase 2: États initialisés', {
    activeTab,
    hasEconomyAccess: hasPermission('member'),
    isFounder: hasPermission('founder'),
    selectedServer: selectedServer?.id
  });

  // Hooks pour les données economy
  const { data: economyData, loading: economyLoading } = useAPI(
    selectedServer ? `/economy/config/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: leaderboardData, loading: leaderboardLoading } = useAPI('/economy/leaderboard');

  const { data: userEconomyData, loading: userEconomyLoading } = useAPI(
    profile ? `/economy/user/${profile.id}` : null,
    [profile?.id]
  );

  useEffect(() => {
    console.log('🔄 Phase 2: Mise à jour des données', {
      economyData,
      leaderboardData,
      userEconomyData,
      loading: economyLoading || leaderboardLoading || userEconomyLoading
    });

    if (economyData) {
      setEconomyConfig(economyData);
      console.log('✅ Phase 2: Configuration économique chargée', economyData);
    }

    if (leaderboardData) {
      setLeaderboards(leaderboardData);
      console.log('✅ Phase 2: Classements chargés', leaderboardData);
    }

    if (userEconomyData) {
      setUserStats(userEconomyData);
      console.log('✅ Phase 2: Stats utilisateur chargées', userEconomyData);
    }

    const isLoading = economyLoading || leaderboardLoading || userEconomyLoading;
    setLoading(isLoading);
    
    if (!isLoading) {
      console.log('🎉 Phase 2: Toutes les données chargées !');
    }
  }, [economyData, leaderboardData, userEconomyData, economyLoading, leaderboardLoading, userEconomyLoading]);

  // Gestion des onglets
  const handleTabChange = (tab) => {
    console.log(`🔄 Phase 2: Changement d'onglet: ${activeTab} -> ${tab}`);
    setActiveTab(tab);
  };

  // Sauvegarde de configuration (Founder+)
  const saveEconomyConfig = async (newConfig) => {
    console.log('💾 Phase 2: Tentative de sauvegarde config', newConfig);
    
    if (!hasPermission('founder')) {
      console.error('❌ Phase 2: Permissions insuffisantes pour modifier la config');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    if (!selectedServer) {
      console.error('❌ Phase 2: Aucun serveur sélectionné');
      addNotification('Veuillez sélectionner un serveur', 'error');
      return;
    }

    try {
      console.log('🚀 Phase 2: Envoi de la configuration au serveur');
      const result = await apiPost(`/economy/config/${selectedServer.id}`, newConfig);
      
      console.log('✅ Phase 2: Configuration sauvegardée avec succès', result);
      setEconomyConfig({ ...economyConfig, ...newConfig });
      addNotification('Configuration économique mise à jour !', 'success');
    } catch (error) {
      console.error('❌ Phase 2: Erreur lors de la sauvegarde', error);
      addNotification('Erreur lors de la sauvegarde', 'error');
    }
  };

  // Interface de chargement
  if (loading) {
    console.log('⏳ Phase 2: Affichage du loader');
    return (
      <div className="economy-manager">
        <div className="economy-header">
          <h2>💰 Système Économique</h2>
          <p>Phase 2 - Economy Manager Avancé</p>
        </div>
        <div className="economy-loading">
          <div className="economy-spinner"></div>
          <p>Chargement des données économiques...</p>
        </div>
      </div>
    );
  }

  // Vérification d'authentification
  if (!isAuthenticated) {
    console.log('🔐 Phase 2: Utilisateur non connecté');
    return (
      <div className="economy-manager">
        <div className="economy-header">
          <h2>💰 Système Économique</h2>
        </div>
        <div className="economy-auth-required">
          <h3>🔐 Connexion Requise</h3>
          <p>Connectez-vous pour accéder au système économique</p>
          <button 
            className="economy-btn-primary"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </div>
    );
  }

  console.log('🎨 Phase 2: Rendu de l\'interface principale');

  return (
    <div className="economy-manager">
      {/* Header */}
      <div className="economy-header">
        <h2>💰 Système Économique Arsenal V4</h2>
        <p>Phase 2 - Economy Manager Complet</p>
        {selectedServer && (
          <div className="economy-server-info">
            <span>Serveur: {selectedServer.name}</span>
            <span className="economy-server-badge">
              {hasPermission('founder') ? 'Founder' : hasPermission('admin') ? 'Admin' : 'Membre'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation des onglets */}
      <div className="economy-tabs">
        <button 
          className={`economy-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          📊 Vue d'ensemble
        </button>
        <button 
          className={`economy-tab ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => handleTabChange('profile')}
        >
          👤 Mon Profil
        </button>
        <button 
          className={`economy-tab ${activeTab === 'leaderboard' ? 'active' : ''}`}
          onClick={() => handleTabChange('leaderboard')}
        >
          🏆 Classements
        </button>
        <button 
          className={`economy-tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => handleTabChange('transactions')}
        >
          📋 Transactions
        </button>
        {hasPermission('founder') && (
          <button 
            className={`economy-tab ${activeTab === 'config' ? 'active' : ''}`}
            onClick={() => handleTabChange('config')}
          >
            ⚙️ Configuration
          </button>
        )}
      </div>

      {/* Contenu des onglets */}
      <div className="economy-content">
        {activeTab === 'overview' && (
          <EconomyOverview 
            config={economyConfig}
            userStats={userStats}
            leaderboards={leaderboards}
          />
        )}
        
        {activeTab === 'profile' && (
          <EconomyProfile 
            userStats={userStats}
            config={economyConfig}
          />
        )}
        
        {activeTab === 'leaderboard' && (
          <EconomyLeaderboard 
            leaderboards={leaderboards}
          />
        )}
        
        {activeTab === 'transactions' && (
          <EconomyTransactions 
            transactions={transactions}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'config' && hasPermission('founder') && (
          <EconomyConfig 
            config={economyConfig}
            onSave={saveEconomyConfig}
            serverId={selectedServer?.id}
          />
        )}
      </div>
    </div>
  );
};

// Composant Vue d'ensemble
const EconomyOverview = ({ config, userStats, leaderboards }) => {
  console.log('📊 Phase 2: Rendu EconomyOverview', { config, userStats, leaderboards });
  
  return (
    <div className="economy-overview">
      <div className="economy-grid">
        {/* Statistiques générales */}
        <div className="economy-card">
          <h3>📊 Statistiques Générales</h3>
          <div className="economy-stats">
            <div className="economy-stat">
              <span className="economy-stat-label">Système activé :</span>
              <span className={`economy-stat-value ${config?.economy?.enabled ? 'enabled' : 'disabled'}`}>
                {config?.economy?.enabled ? '✅ Oui' : '❌ Non'}
              </span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Bonus quotidien :</span>
              <span className="economy-stat-value">
                💰 {config?.economy?.daily_amount || 100}
              </span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Gains travail :</span>
              <span className="economy-stat-value">
                💼 {config?.economy?.work_range?.[0] || 50} - {config?.economy?.work_range?.[1] || 150}
              </span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Système niveaux :</span>
              <span className={`economy-stat-value ${config?.levels?.enabled ? 'enabled' : 'disabled'}`}>
                {config?.levels?.enabled ? '✅ Oui' : '❌ Non'}
              </span>
            </div>
          </div>
        </div>

        {/* Profil utilisateur rapide */}
        {userStats && (
          <div className="economy-card">
            <h3>👤 Votre Profil</h3>
            <div className="economy-user-quick">
              <div className="economy-balance">
                <span className="economy-balance-label">Solde total :</span>
                <span className="economy-balance-value">
                  💰 {userStats.economy?.total_balance || 0}
                </span>
              </div>
              <div className="economy-level">
                <span className="economy-level-label">Niveau :</span>
                <span className="economy-level-value">
                  ⭐ {userStats.levels?.level || 1}
                </span>
              </div>
              <div className="economy-progress">
                <span className="economy-progress-label">Progression XP :</span>
                <div className="economy-progress-bar">
                  <div 
                    className="economy-progress-fill"
                    style={{ width: `${userStats.levels?.xp_progress || 0}%` }}
                  ></div>
                </div>
                <span className="economy-progress-text">
                  {userStats.levels?.xp_progress || 0}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Top 3 classement */}
        {leaderboards?.balance_leaderboard && (
          <div className="economy-card">
            <h3>🏆 Top Balance</h3>
            <div className="economy-top3">
              {leaderboards.balance_leaderboard.slice(0, 3).map((user, index) => (
                <div key={user.user_id} className={`economy-top-user rank-${index + 1}`}>
                  <span className="economy-rank">{index + 1}</span>
                  <span className="economy-username">{user.username}</span>
                  <span className="economy-amount">💰 {user.total_balance}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Composant Profil utilisateur
const EconomyProfile = ({ userStats, config }) => {
  console.log('👤 Phase 2: Rendu EconomyProfile', { userStats, config });
  
  if (!userStats) {
    return (
      <div className="economy-profile">
        <div className="economy-no-data">
          <h3>📊 Profil Économique</h3>
          <p>Aucune donnée économique trouvée pour votre compte.</p>
          <p>Commencez à utiliser les commandes économiques sur Discord !</p>
        </div>
      </div>
    );
  }

  return (
    <div className="economy-profile">
      <div className="economy-grid">
        {/* Soldes */}
        <div className="economy-card">
          <h3>💰 Vos Soldes</h3>
          <div className="economy-balances">
            <div className="economy-balance-item">
              <span className="economy-balance-icon">💵</span>
              <div className="economy-balance-info">
                <span className="economy-balance-label">Portefeuille</span>
                <span className="economy-balance-amount">{userStats.economy?.balance || 0}</span>
              </div>
            </div>
            <div className="economy-balance-item">
              <span className="economy-balance-icon">🏦</span>
              <div className="economy-balance-info">
                <span className="economy-balance-label">Banque</span>
                <span className="economy-balance-amount">{userStats.economy?.bank_balance || 0}</span>
              </div>
            </div>
            <div className="economy-balance-item total">
              <span className="economy-balance-icon">💎</span>
              <div className="economy-balance-info">
                <span className="economy-balance-label">Total</span>
                <span className="economy-balance-amount">{userStats.economy?.total_balance || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Niveaux */}
        <div className="economy-card">
          <h3>⭐ Progression</h3>
          <div className="economy-levels">
            <div className="economy-level-main">
              <span className="economy-level-number">{userStats.levels?.level || 1}</span>
              <div className="economy-level-info">
                <span className="economy-level-label">Niveau actuel</span>
                <div className="economy-xp-bar">
                  <div 
                    className="economy-xp-fill"
                    style={{ width: `${userStats.levels?.xp_progress || 0}%` }}
                  ></div>
                </div>
                <span className="economy-xp-text">
                  {userStats.levels?.xp || 0} / {userStats.levels?.xp_needed || 150} XP
                </span>
              </div>
            </div>
            <div className="economy-level-stats">
              <div className="economy-level-stat">
                <span className="economy-stat-label">Messages envoyés :</span>
                <span className="economy-stat-value">{userStats.levels?.messages_sent || 0}</span>
              </div>
              <div className="economy-level-stat">
                <span className="economy-stat-label">Temps vocal :</span>
                <span className="economy-stat-value">{Math.floor((userStats.levels?.voice_time || 0) / 60)} min</span>
              </div>
            </div>
          </div>
        </div>

        {/* Statistiques économiques */}
        <div className="economy-card">
          <h3>📊 Statistiques</h3>
          <div className="economy-user-stats">
            <div className="economy-stat">
              <span className="economy-stat-label">Série quotidienne :</span>
              <span className="economy-stat-value">🔥 {userStats.economy?.daily_streak || 0} jours</span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Total gagné :</span>
              <span className="economy-stat-value">💸 {userStats.economy?.total_earned || 0}</span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Total dépensé :</span>
              <span className="economy-stat-value">💳 {userStats.economy?.total_spent || 0}</span>
            </div>
            <div className="economy-stat">
              <span className="economy-stat-label">Valeur nette :</span>
              <span className="economy-stat-value">💎 {userStats.economy?.net_worth || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Composant Classements
const EconomyLeaderboard = ({ leaderboards }) => {
  console.log('🏆 Phase 2: Rendu EconomyLeaderboard', { leaderboards });
  
  const [activeLeaderboard, setActiveLeaderboard] = useState('balance');

  return (
    <div className="economy-leaderboard">
      <div className="economy-leaderboard-tabs">
        <button 
          className={`economy-leaderboard-tab ${activeLeaderboard === 'balance' ? 'active' : ''}`}
          onClick={() => setActiveLeaderboard('balance')}
        >
          💰 Richesse
        </button>
        <button 
          className={`economy-leaderboard-tab ${activeLeaderboard === 'level' ? 'active' : ''}`}
          onClick={() => setActiveLeaderboard('level')}
        >
          ⭐ Niveaux
        </button>
      </div>

      <div className="economy-leaderboard-content">
        {activeLeaderboard === 'balance' && leaderboards?.balance_leaderboard && (
          <div className="economy-leaderboard-list">
            <h3>🏆 Classement par Richesse</h3>
            {leaderboards.balance_leaderboard.map((user, index) => (
              <div key={user.user_id} className={`economy-leaderboard-item rank-${index + 1}`}>
                <span className="economy-rank">#{index + 1}</span>
                <span className="economy-username">{user.username}</span>
                <div className="economy-user-info">
                  <span className="economy-balance">💰 {user.total_balance}</span>
                  <span className="economy-streak">🔥 {user.daily_streak} jours</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeLeaderboard === 'level' && leaderboards?.level_leaderboard && (
          <div className="economy-leaderboard-list">
            <h3>⭐ Classement par Niveau</h3>
            {leaderboards.level_leaderboard.map((user, index) => (
              <div key={user.user_id} className={`economy-leaderboard-item rank-${index + 1}`}>
                <span className="economy-rank">#{index + 1}</span>
                <span className="economy-username">{user.username}</span>
                <div className="economy-user-info">
                  <span className="economy-level">⭐ Niveau {user.level}</span>
                  <span className="economy-xp">✨ {user.total_xp} XP</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Composant Transactions (placeholder pour Phase 3)
const EconomyTransactions = ({ transactions, serverId }) => {
  console.log('📋 Phase 2: Rendu EconomyTransactions', { transactions, serverId });
  
  return (
    <div className="economy-transactions">
      <h3>📋 Historique des Transactions</h3>
      <div className="economy-coming-soon">
        <p>🚧 Interface de transactions en développement</p>
        <p>Cette section affichera prochainement :</p>
        <ul>
          <li>📊 Historique détaillé des transactions</li>
          <li>🔍 Filtres par type et période</li>
          <li>📈 Graphiques d'évolution</li>
          <li>💸 Analyse des dépenses</li>
        </ul>
      </div>
    </div>
  );
};

// Composant Configuration (Founder uniquement)
const EconomyConfig = ({ config, onSave, serverId }) => {
  console.log('⚙️ Phase 2: Rendu EconomyConfig', { config, serverId });
  
  const [configForm, setConfigForm] = useState({
    economy: {
      enabled: config?.economy?.enabled || true,
      daily_amount: config?.economy?.daily_amount || 100,
      work_range: config?.economy?.work_range || [50, 150],
      crime_range: config?.economy?.crime_range || [100, 300],
      crime_fail_penalty: config?.economy?.crime_fail_penalty || 50,
      bank_interest_rate: config?.economy?.bank_interest_rate || 0.02
    },
    levels: {
      enabled: config?.levels?.enabled || true,
      xp_per_message: config?.levels?.xp_per_message || 15,
      xp_per_minute_voice: config?.levels?.xp_per_minute_voice || 10,
      level_up_bonus: config?.levels?.level_up_bonus || 50
    }
  });

  const handleConfigChange = (section, field, value) => {
    console.log(`🔄 Phase 2: Modification config ${section}.${field} = ${value}`);
    setConfigForm(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSave = () => {
    console.log('💾 Phase 2: Sauvegarde configuration', configForm);
    onSave(configForm);
  };

  return (
    <div className="economy-config">
      <h3>⚙️ Configuration Économique</h3>
      
      <div className="economy-config-sections">
        {/* Configuration économie */}
        <div className="economy-config-section">
          <h4>💰 Système Économique</h4>
          
          <div className="economy-config-group">
            <label className="economy-config-label">
              <input
                type="checkbox"
                checked={configForm.economy.enabled}
                onChange={(e) => handleConfigChange('economy', 'enabled', e.target.checked)}
              />
              Activer le système économique
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              Bonus quotidien :
              <input
                type="number"
                value={configForm.economy.daily_amount}
                onChange={(e) => handleConfigChange('economy', 'daily_amount', parseInt(e.target.value))}
                min="1"
                max="1000"
              />
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              Gains travail (min) :
              <input
                type="number"
                value={configForm.economy.work_range[0]}
                onChange={(e) => handleConfigChange('economy', 'work_range', [parseInt(e.target.value), configForm.economy.work_range[1]])}
                min="1"
                max="500"
              />
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              Gains travail (max) :
              <input
                type="number"
                value={configForm.economy.work_range[1]}
                onChange={(e) => handleConfigChange('economy', 'work_range', [configForm.economy.work_range[0], parseInt(e.target.value)])}
                min="1"
                max="1000"
              />
            </label>
          </div>
        </div>

        {/* Configuration niveaux */}
        <div className="economy-config-section">
          <h4>⭐ Système de Niveaux</h4>
          
          <div className="economy-config-group">
            <label className="economy-config-label">
              <input
                type="checkbox"
                checked={configForm.levels.enabled}
                onChange={(e) => handleConfigChange('levels', 'enabled', e.target.checked)}
              />
              Activer le système de niveaux
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              XP par message :
              <input
                type="number"
                value={configForm.levels.xp_per_message}
                onChange={(e) => handleConfigChange('levels', 'xp_per_message', parseInt(e.target.value))}
                min="1"
                max="100"
              />
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              XP par minute vocal :
              <input
                type="number"
                value={configForm.levels.xp_per_minute_voice}
                onChange={(e) => handleConfigChange('levels', 'xp_per_minute_voice', parseInt(e.target.value))}
                min="1"
                max="100"
              />
            </label>
          </div>

          <div className="economy-config-group">
            <label className="economy-config-label">
              Bonus de niveau :
              <input
                type="number"
                value={configForm.levels.level_up_bonus}
                onChange={(e) => handleConfigChange('levels', 'level_up_bonus', parseInt(e.target.value))}
                min="0"
                max="1000"
              />
            </label>
          </div>
        </div>
      </div>

      <div className="economy-config-actions">
        <button 
          className="economy-btn-primary"
          onClick={handleSave}
        >
          💾 Sauvegarder la Configuration
        </button>
        <button 
          className="economy-btn-secondary"
          onClick={() => setConfigForm(config)}
        >
          🔄 Réinitialiser
        </button>
      </div>
    </div>
  );
};

export default EconomyManager;
