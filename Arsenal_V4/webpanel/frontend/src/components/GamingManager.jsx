import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAPI, apiPost, apiDelete } from '../hooks/useAPI';
import './GamingManager.css';

const GamingManager = () => {
  console.log('🎮 Phase 5: Initialisation GamingManager');
  
  const { 
    isAuthenticated, 
    hasPermission, 
    selectedServer, 
    addNotification,
    profile 
  } = useApp();

  // États locaux
  const [activeTab, setActiveTab] = useState('levels');
  const [levelStats, setLevelStats] = useState([]);
  const [gamingConfig, setGamingConfig] = useState(null);
  const [minigameStats, setMinigameStats] = useState([]);
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);

  console.log('📊 Phase 5: États initialisés', {
    activeTab,
    hasGamingAccess: hasPermission('member'),
    isAdmin: hasPermission('admin'),
    selectedServer: selectedServer?.id
  });

  // Hooks pour les données gaming
  const { data: levelsData, loading: levelsLoading } = useAPI(
    selectedServer ? `/gaming/levels/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: configData, loading: configLoading } = useAPI(
    selectedServer ? `/gaming/config/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: minigamesData, loading: minigamesLoading } = useAPI(
    selectedServer ? `/gaming/minigames/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: rewardsData, loading: rewardsLoading } = useAPI(
    selectedServer ? `/gaming/rewards/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  useEffect(() => {
    console.log('🔄 Phase 5: Mise à jour des données', {
      levelsData,
      configData,
      minigamesData,
      rewardsData,
      loading: levelsLoading || configLoading || minigamesLoading || rewardsLoading
    });

    if (levelsData) {
      setLevelStats(levelsData.levels || []);
      console.log('✅ Phase 5: Stats de niveau chargées', levelsData);
    }

    if (configData) {
      setGamingConfig(configData.config || {});
      console.log('✅ Phase 5: Configuration gaming chargée', configData);
    }

    if (minigamesData) {
      setMinigameStats(minigamesData.minigames || []);
      console.log('✅ Phase 5: Stats mini-jeux chargées', minigamesData);
    }

    if (rewardsData) {
      setRewards(rewardsData.rewards || []);
      console.log('✅ Phase 5: Récompenses chargées', rewardsData);
    }

    const isLoading = levelsLoading || configLoading || minigamesLoading || rewardsLoading;
    setLoading(isLoading);
    
    if (!isLoading) {
      console.log('🎉 Phase 5: Toutes les données chargées !');
    }
  }, [levelsData, configData, minigamesData, rewardsData, levelsLoading, configLoading, minigamesLoading, rewardsLoading]);

  // Gestion des onglets
  const handleTabChange = (tab) => {
    console.log(`🔄 Phase 5: Changement d'onglet: ${activeTab} -> ${tab}`);
    setActiveTab(tab);
  };

  // Gain d'XP manuel (Admin+)
  const giveXP = async (userId, amount, reason = 'Manuel') => {
    console.log('⭐ Phase 5: Attribution XP', { userId, amount, reason });
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 5: Permissions insuffisantes pour donner XP');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/gaming/xp/${selectedServer.id}`, {
        user_id: userId,
        amount: parseInt(amount),
        reason,
        given_by: profile?.id
      });
      
      console.log('✅ Phase 5: XP attribué avec succès', result);
      addNotification(`${amount} XP attribué avec succès !`, 'success');
      
      // Recharger les données
      window.location.reload();
    } catch (error) {
      console.error('❌ Phase 5: Erreur lors de l\'attribution XP', error);
      addNotification('Erreur lors de l\'attribution d\'XP', 'error');
    }
  };

  // Ajout de récompense (Admin+)
  const addReward = async (level, type, value) => {
    console.log('🎁 Phase 5: Ajout récompense', { level, type, value });
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 5: Permissions insuffisantes pour ajouter récompense');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/gaming/rewards/${selectedServer.id}`, {
        level: parseInt(level),
        reward_type: type,
        reward_value: value
      });
      
      console.log('✅ Phase 5: Récompense ajoutée avec succès', result);
      addNotification('Récompense ajoutée avec succès !', 'success');
      
      // Recharger les données
      window.location.reload();
    } catch (error) {
      console.error('❌ Phase 5: Erreur lors de l\'ajout de récompense', error);
      addNotification('Erreur lors de l\'ajout de récompense', 'error');
    }
  };

  // Sauvegarde configuration (Admin+)
  const saveGamingConfig = async (newConfig) => {
    console.log('💾 Phase 5: Tentative de sauvegarde config gaming', newConfig);
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 5: Permissions insuffisantes pour modifier la config');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/gaming/config/${selectedServer.id}`, newConfig);
      console.log('✅ Phase 5: Configuration sauvegardée avec succès', result);
      setGamingConfig({ ...gamingConfig, ...newConfig });
      addNotification('Configuration gaming mise à jour !', 'success');
    } catch (error) {
      console.error('❌ Phase 5: Erreur lors de la sauvegarde', error);
      addNotification('Erreur lors de la sauvegarde', 'error');
    }
  };

  // Interface de chargement
  if (loading) {
    console.log('⏳ Phase 5: Affichage du loader');
    return (
      <div className="gaming-manager">
        <div className="gaming-header">
          <h2>🎮 Système Gaming</h2>
          <p>Phase 5 - Gaming Manager Avancé</p>
        </div>
        <div className="gaming-loading">
          <div className="gaming-spinner"></div>
          <p>Chargement des données gaming...</p>
        </div>
      </div>
    );
  }

  // Vérification d'authentification
  if (!isAuthenticated) {
    console.log('🔐 Phase 5: Utilisateur non connecté');
    return (
      <div className="gaming-manager">
        <div className="gaming-header">
          <h2>🎮 Système Gaming</h2>
        </div>
        <div className="gaming-auth-required">
          <h3>🔐 Connexion Requise</h3>
          <p>Connectez-vous pour accéder au système gaming</p>
          <button 
            className="gaming-btn-primary"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </div>
    );
  }

  console.log('🎨 Phase 5: Rendu de l\'interface principale');

  return (
    <div className="gaming-manager">
      {/* Header */}
      <div className="gaming-header">
        <h2>🎮 Système Gaming Arsenal V4</h2>
        <p>Phase 5 - Gaming Manager Complet</p>
        {selectedServer && (
          <div className="gaming-server-info">
            <span>Serveur: {selectedServer.name}</span>
            <span className="gaming-server-badge">
              {hasPermission('founder') ? 'Founder' : hasPermission('admin') ? 'Admin' : 'Membre'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation des onglets */}
      <div className="gaming-tabs">
        <button 
          className={`gaming-tab ${activeTab === 'levels' ? 'active' : ''}`}
          onClick={() => handleTabChange('levels')}
        >
          ⭐ Niveaux
        </button>
        <button 
          className={`gaming-tab ${activeTab === 'leaderboard' ? 'active' : ''}`}
          onClick={() => handleTabChange('leaderboard')}
        >
          🏆 Classement
        </button>
        <button 
          className={`gaming-tab ${activeTab === 'minigames' ? 'active' : ''}`}
          onClick={() => handleTabChange('minigames')}
        >
          🎲 Mini-jeux
        </button>
        <button 
          className={`gaming-tab ${activeTab === 'rewards' ? 'active' : ''}`}
          onClick={() => handleTabChange('rewards')}
        >
          🎁 Récompenses
        </button>
        {hasPermission('admin') && (
          <>
            <button 
              className={`gaming-tab ${activeTab === 'management' ? 'active' : ''}`}
              onClick={() => handleTabChange('management')}
            >
              ⚙️ Gestion
            </button>
            <button 
              className={`gaming-tab ${activeTab === 'config' ? 'active' : ''}`}
              onClick={() => handleTabChange('config')}
            >
              🔧 Configuration
            </button>
          </>
        )}
      </div>

      {/* Contenu des onglets */}
      <div className="gaming-content">
        {activeTab === 'levels' && (
          <GamingLevels 
            levels={levelStats}
            config={gamingConfig}
          />
        )}
        
        {activeTab === 'leaderboard' && (
          <GamingLeaderboard 
            levels={levelStats}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'minigames' && (
          <GamingMinigames 
            minigames={minigameStats}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'rewards' && (
          <GamingRewards 
            rewards={rewards}
            onAddReward={addReward}
            hasAdmin={hasPermission('admin')}
          />
        )}
        
        {activeTab === 'management' && hasPermission('admin') && (
          <GamingManagement 
            onGiveXP={giveXP}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'config' && hasPermission('admin') && (
          <GamingConfig 
            config={gamingConfig}
            onSave={saveGamingConfig}
          />
        )}
      </div>
    </div>
  );
};

// Composant Niveaux
const GamingLevels = ({ levels, config }) => {
  console.log('⭐ Phase 5: Rendu GamingLevels', { levels, config });

  const calculateXPForLevel = (level) => {
    return Math.floor(100 * Math.pow(1.5, level - 1));
  };

  const getLevelProgress = (currentXP, level) => {
    const currentLevelXP = calculateXPForLevel(level);
    const nextLevelXP = calculateXPForLevel(level + 1);
    const progress = ((currentXP - currentLevelXP) / (nextLevelXP - currentLevelXP)) * 100;
    return Math.max(0, Math.min(100, progress));
  };

  return (
    <div className="gaming-levels">
      <div className="gaming-overview-stats">
        <div className="gaming-stat-card">
          <h3>📊 Statistiques Générales</h3>
          <div className="gaming-stats-grid">
            <div className="gaming-stat-item">
              <span className="gaming-stat-value">{levels.length}</span>
              <span className="gaming-stat-label">Utilisateurs actifs</span>
            </div>
            <div className="gaming-stat-item">
              <span className="gaming-stat-value">
                {levels.reduce((sum, level) => sum + level.level, 0)}
              </span>
              <span className="gaming-stat-label">Niveaux cumulés</span>
            </div>
            <div className="gaming-stat-item">
              <span className="gaming-stat-value">
                {levels.reduce((sum, level) => sum + level.total_xp, 0).toLocaleString()}
              </span>
              <span className="gaming-stat-label">XP total</span>
            </div>
            <div className="gaming-stat-item">
              <span className="gaming-stat-value">
                {Math.max(...levels.map(l => l.level), 0)}
              </span>
              <span className="gaming-stat-label">Niveau max</span>
            </div>
          </div>
        </div>
      </div>

      {levels.length > 0 ? (
        <div className="gaming-levels-list">
          <h3>⭐ Progression des Utilisateurs</h3>
          {levels.slice(0, 20).map((levelData, index) => {
            const progress = getLevelProgress(levelData.total_xp, levelData.level);
            const nextLevelXP = calculateXPForLevel(levelData.level + 1);
            const currentLevelXP = calculateXPForLevel(levelData.level);
            const xpNeeded = nextLevelXP - levelData.total_xp;

            return (
              <div key={levelData.user_id || index} className="gaming-level-item">
                <div className="gaming-level-info">
                  <div className="gaming-level-avatar">
                    <span className="gaming-level-rank">#{index + 1}</span>
                  </div>
                  <div className="gaming-level-details">
                    <span className="gaming-level-username">
                      {levelData.username || `Utilisateur ${levelData.user_id?.slice(-4)}`}
                    </span>
                    <div className="gaming-level-stats">
                      <span className="gaming-level-badge">Niveau {levelData.level}</span>
                      <span className="gaming-level-xp">
                        {levelData.total_xp.toLocaleString()} XP
                      </span>
                      <span className="gaming-level-messages">
                        {levelData.messages_count} messages
                      </span>
                    </div>
                  </div>
                </div>
                <div className="gaming-level-progress">
                  <div className="gaming-progress-bar">
                    <div 
                      className="gaming-progress-fill"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <span className="gaming-progress-text">
                    {xpNeeded > 0 ? `${xpNeeded.toLocaleString()} XP manquant` : 'Niveau max !'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="gaming-no-data">
          <p>📊 Aucune donnée de niveau disponible</p>
          <p>Les statistiques apparaîtront quand les utilisateurs gagneront de l'XP</p>
        </div>
      )}
    </div>
  );
};

// Placeholders pour les autres composants (à implémenter)
const GamingLeaderboard = ({ levels, serverId }) => (
  <div className="gaming-leaderboard">
    <h3>🏆 Classement Global</h3>
    <div className="gaming-coming-soon">
      <p>🚧 Interface de classement en développement</p>
      <p>Cette section affichera :</p>
      <ul>
        <li>🏆 Top des utilisateurs par niveau</li>
        <li>📊 Classements multiples (XP, messages, vocal)</li>
        <li>🎖️ Récompenses de rang</li>
        <li>📈 Évolution temporelle</li>
      </ul>
    </div>
  </div>
);

const GamingMinigames = ({ minigames, serverId }) => (
  <div className="gaming-minigames">
    <h3>🎲 Mini-jeux</h3>
    <div className="gaming-coming-soon">
      <p>🚧 Interface de mini-jeux en développement</p>
      <p>Cette section proposera :</p>
      <ul>
        <li>🎯 Jeux de réflexe et rapidité</li>
        <li>🧩 Défis de logique</li>
        <li>💰 Jeux de chance avec récompenses</li>
        <li>🏆 Tournois et compétitions</li>
      </ul>
    </div>
  </div>
);

const GamingRewards = ({ rewards, onAddReward, hasAdmin }) => (
  <div className="gaming-rewards">
    <h3>🎁 Système de Récompenses</h3>
    <div className="gaming-coming-soon">
      <p>🚧 Interface de récompenses en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>🎁 Configuration des récompenses par niveau</li>
        <li>🏷️ Rôles automatiques</li>
        <li>💰 Récompenses économiques</li>
        <li>🎖️ Badges et titres personnalisés</li>
      </ul>
    </div>
  </div>
);

const GamingManagement = ({ onGiveXP, serverId }) => (
  <div className="gaming-management">
    <h3>⚙️ Gestion Gaming</h3>
    <div className="gaming-coming-soon">
      <p>🚧 Interface de gestion en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⭐ Attribution manuelle d'XP</li>
        <li>🔄 Reset de niveaux</li>
        <li>📊 Statistiques détaillées</li>
        <li>🛠️ Outils d'administration</li>
      </ul>
    </div>
  </div>
);

const GamingConfig = ({ config, onSave }) => (
  <div className="gaming-config">
    <h3>🔧 Configuration Gaming</h3>
    <div className="gaming-coming-soon">
      <p>🚧 Interface de configuration en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⭐ Paramètres de gain d'XP</li>
        <li>📈 Formules de progression</li>
        <li>🎮 Activation des fonctionnalités</li>
        <li>🔧 Personnalisation avancée</li>
      </ul>
    </div>
  </div>
);

export default GamingManager;
