import React, { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAPI, apiPost, apiDelete } from '../hooks/useAPI';
import './MusicManager.css';

const MusicManager = () => {
  console.log('🎵 Phase 4: Initialisation MusicManager');
  
  const { 
    isAuthenticated, 
    hasPermission, 
    selectedServer, 
    addNotification,
    profile 
  } = useApp();

  // États locaux
  const [activeTab, setActiveTab] = useState('player');
  const [currentQueue, setCurrentQueue] = useState([]);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [playbackStatus, setPlaybackStatus] = useState({
    isPlaying: false,
    volume: 50,
    position: 0,
    duration: 0,
    repeat: 'none',
    shuffle: false
  });
  const [musicConfig, setMusicConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  console.log('📊 Phase 4: États initialisés', {
    activeTab,
    hasMusicAccess: hasPermission('member'),
    isAdmin: hasPermission('admin'),
    selectedServer: selectedServer?.id,
    queueLength: currentQueue.length
  });

  // Hooks pour les données musicales
  const { data: queueData, loading: queueLoading } = useAPI(
    selectedServer ? `/music/queue/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: statusData, loading: statusLoading } = useAPI(
    selectedServer ? `/music/status/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  const { data: configData, loading: configLoading } = useAPI(
    selectedServer ? `/music/config/${selectedServer.id}` : null,
    [selectedServer?.id]
  );

  useEffect(() => {
    console.log('🔄 Phase 4: Mise à jour des données', {
      queueData,
      statusData,
      configData,
      loading: queueLoading || statusLoading || configLoading
    });

    if (queueData) {
      setCurrentQueue(queueData.queue || []);
      setCurrentTrack(queueData.current_track || null);
      console.log('✅ Phase 4: Queue musicale chargée', queueData);
    }

    if (statusData) {
      setPlaybackStatus(statusData.status || {});
      console.log('✅ Phase 4: Statut de lecture chargé', statusData);
    }

    if (configData) {
      setMusicConfig(configData.config || {});
      console.log('✅ Phase 4: Configuration musicale chargée', configData);
    }

    const isLoading = queueLoading || statusLoading || configLoading;
    setLoading(isLoading);
    
    if (!isLoading) {
      console.log('🎉 Phase 4: Toutes les données chargées !');
    }
  }, [queueData, statusData, configData, queueLoading, statusLoading, configLoading]);

  // Gestion des onglets
  const handleTabChange = (tab) => {
    console.log(`🔄 Phase 4: Changement d'onglet: ${activeTab} -> ${tab}`);
    setActiveTab(tab);
  };

  // Contrôles de lecture
  const handlePlayPause = async () => {
    console.log('⏯️ Phase 4: Toggle play/pause');
    try {
      const result = await apiPost(`/music/control/${selectedServer.id}`, {
        action: playbackStatus.isPlaying ? 'pause' : 'play'
      });
      console.log('✅ Phase 4: Contrôle exécuté', result);
      addNotification(playbackStatus.isPlaying ? 'Lecture mise en pause' : 'Lecture reprise', 'info');
    } catch (error) {
      console.error('❌ Phase 4: Erreur contrôle lecture', error);
      addNotification('Erreur lors du contrôle de lecture', 'error');
    }
  };

  const handleSkip = async (direction = 'next') => {
    console.log(`⏭️ Phase 4: Skip ${direction}`);
    try {
      const result = await apiPost(`/music/control/${selectedServer.id}`, {
        action: direction === 'next' ? 'skip' : 'previous'
      });
      console.log('✅ Phase 4: Skip exécuté', result);
      addNotification(`Piste ${direction === 'next' ? 'suivante' : 'précédente'}`, 'info');
    } catch (error) {
      console.error('❌ Phase 4: Erreur skip', error);
      addNotification('Erreur lors du changement de piste', 'error');
    }
  };

  const handleVolumeChange = async (volume) => {
    console.log(`🔊 Phase 4: Changement volume: ${volume}`);
    try {
      const result = await apiPost(`/music/control/${selectedServer.id}`, {
        action: 'volume',
        value: volume
      });
      setPlaybackStatus(prev => ({ ...prev, volume }));
      console.log('✅ Phase 4: Volume modifié', result);
    } catch (error) {
      console.error('❌ Phase 4: Erreur volume', error);
      addNotification('Erreur lors du changement de volume', 'error');
    }
  };

  // Ajout de musique
  const addToQueue = async (url, requestedBy = profile?.username) => {
    console.log('➕ Phase 4: Ajout à la queue', { url, requestedBy });
    
    if (!url.trim()) {
      addNotification('Veuillez entrer une URL ou un terme de recherche', 'error');
      return;
    }

    try {
      const result = await apiPost(`/music/add/${selectedServer.id}`, {
        url: url.trim(),
        requested_by: requestedBy || 'Inconnu'
      });
      console.log('✅ Phase 4: Musique ajoutée', result);
      addNotification('Musique ajoutée à la queue !', 'success');
      
      // Recharger les données
      window.location.reload();
    } catch (error) {
      console.error('❌ Phase 4: Erreur ajout musique', error);
      addNotification('Erreur lors de l\'ajout de la musique', 'error');
    }
  };

  // Sauvegarde configuration (Admin+)
  const saveMusicConfig = async (newConfig) => {
    console.log('💾 Phase 4: Tentative de sauvegarde config musicale', newConfig);
    
    if (!hasPermission('admin')) {
      console.error('❌ Phase 4: Permissions insuffisantes pour modifier la config');
      addNotification('Permissions insuffisantes', 'error');
      return;
    }

    try {
      const result = await apiPost(`/music/config/${selectedServer.id}`, newConfig);
      console.log('✅ Phase 4: Configuration sauvegardée avec succès', result);
      setMusicConfig({ ...musicConfig, ...newConfig });
      addNotification('Configuration musicale mise à jour !', 'success');
    } catch (error) {
      console.error('❌ Phase 4: Erreur lors de la sauvegarde', error);
      addNotification('Erreur lors de la sauvegarde', 'error');
    }
  };

  // Interface de chargement
  if (loading) {
    console.log('⏳ Phase 4: Affichage du loader');
    return (
      <div className="music-manager">
        <div className="music-header">
          <h2>🎵 Système Musical</h2>
          <p>Phase 4 - Music Manager Avancé</p>
        </div>
        <div className="music-loading">
          <div className="music-spinner"></div>
          <p>Chargement des données musicales...</p>
        </div>
      </div>
    );
  }

  // Vérification d'authentification
  if (!isAuthenticated) {
    console.log('🔐 Phase 4: Utilisateur non connecté');
    return (
      <div className="music-manager">
        <div className="music-header">
          <h2>🎵 Système Musical</h2>
        </div>
        <div className="music-auth-required">
          <h3>🔐 Connexion Requise</h3>
          <p>Connectez-vous pour accéder au système musical</p>
          <button 
            className="music-btn-primary"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </div>
    );
  }

  console.log('🎨 Phase 4: Rendu de l\'interface principale');

  return (
    <div className="music-manager">
      {/* Header */}
      <div className="music-header">
        <h2>🎵 Système Musical Arsenal V4</h2>
        <p>Phase 4 - Music Manager Complet</p>
        {selectedServer && (
          <div className="music-server-info">
            <span>Serveur: {selectedServer.name}</span>
            <span className="music-server-badge">
              {hasPermission('founder') ? 'Founder' : hasPermission('admin') ? 'Admin' : 'Membre'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation des onglets */}
      <div className="music-tabs">
        <button 
          className={`music-tab ${activeTab === 'player' ? 'active' : ''}`}
          onClick={() => handleTabChange('player')}
        >
          🎧 Lecteur
        </button>
        <button 
          className={`music-tab ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={() => handleTabChange('queue')}
        >
          📋 Queue
        </button>
        <button 
          className={`music-tab ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => handleTabChange('search')}
        >
          🔍 Recherche
        </button>
        <button 
          className={`music-tab ${activeTab === 'playlists' ? 'active' : ''}`}
          onClick={() => handleTabChange('playlists')}
        >
          📚 Playlists
        </button>
        {hasPermission('admin') && (
          <button 
            className={`music-tab ${activeTab === 'config' ? 'active' : ''}`}
            onClick={() => handleTabChange('config')}
          >
            ⚙️ Configuration
          </button>
        )}
      </div>

      {/* Contenu des onglets */}
      <div className="music-content">
        {activeTab === 'player' && (
          <MusicPlayer 
            currentTrack={currentTrack}
            playbackStatus={playbackStatus}
            onPlayPause={handlePlayPause}
            onSkip={handleSkip}
            onVolumeChange={handleVolumeChange}
          />
        )}
        
        {activeTab === 'queue' && (
          <MusicQueue 
            queue={currentQueue}
            currentTrack={currentTrack}
            onAddToQueue={addToQueue}
          />
        )}
        
        {activeTab === 'search' && (
          <MusicSearch 
            onAddToQueue={addToQueue}
            serverId={selectedServer?.id}
          />
        )}
        
        {activeTab === 'playlists' && (
          <MusicPlaylists 
            serverId={selectedServer?.id}
            onAddToQueue={addToQueue}
          />
        )}
        
        {activeTab === 'config' && hasPermission('admin') && (
          <MusicConfig 
            config={musicConfig}
            onSave={saveMusicConfig}
          />
        )}
      </div>
    </div>
  );
};

// Composant Lecteur Musical
const MusicPlayer = ({ currentTrack, playbackStatus, onPlayPause, onSkip, onVolumeChange }) => {
  console.log('🎧 Phase 4: Rendu MusicPlayer', { currentTrack, playbackStatus });

  const formatTime = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = playbackStatus.duration > 0 
    ? (playbackStatus.position / playbackStatus.duration) * 100 
    : 0;

  return (
    <div className="music-player">
      <div className="music-player-main">
        {/* Informations de la piste */}
        <div className="music-track-info">
          {currentTrack ? (
            <>
              <div className="music-track-thumbnail">
                {currentTrack.thumbnail ? (
                  <img src={currentTrack.thumbnail} alt={currentTrack.title} />
                ) : (
                  <div className="music-track-placeholder">🎵</div>
                )}
              </div>
              <div className="music-track-details">
                <h3 className="music-track-title">{currentTrack.title}</h3>
                <p className="music-track-artist">{currentTrack.artist || currentTrack.uploader}</p>
                <p className="music-track-duration">{formatTime(currentTrack.duration)}</p>
                <p className="music-track-requester">
                  Demandé par: {currentTrack.requested_by}
                </p>
              </div>
            </>
          ) : (
            <div className="music-no-track">
              <div className="music-track-placeholder">🎵</div>
              <div className="music-track-details">
                <h3>Aucune musique en cours</h3>
                <p>Ajoutez des pistes à la queue pour commencer</p>
              </div>
            </div>
          )}
        </div>

        {/* Contrôles de lecture */}
        <div className="music-controls">
          <button 
            className="music-control-btn"
            onClick={() => onSkip('previous')}
            disabled={!currentTrack}
          >
            ⏮️
          </button>
          <button 
            className="music-control-btn music-play-pause"
            onClick={onPlayPause}
            disabled={!currentTrack}
          >
            {playbackStatus.isPlaying ? '⏸️' : '▶️'}
          </button>
          <button 
            className="music-control-btn"
            onClick={() => onSkip('next')}
            disabled={!currentTrack}
          >
            ⏭️
          </button>
        </div>

        {/* Barre de progression */}
        <div className="music-progress-container">
          <span className="music-time">{formatTime(playbackStatus.position)}</span>
          <div className="music-progress-bar">
            <div 
              className="music-progress-fill"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
          <span className="music-time">{formatTime(playbackStatus.duration)}</span>
        </div>

        {/* Contrôles de volume */}
        <div className="music-volume-container">
          <span className="music-volume-icon">🔊</span>
          <input
            type="range"
            min="0"
            max="100"
            value={playbackStatus.volume || 50}
            onChange={(e) => onVolumeChange(parseInt(e.target.value))}
            className="music-volume-slider"
          />
          <span className="music-volume-value">{playbackStatus.volume || 50}%</span>
        </div>
      </div>
    </div>
  );
};

// Composant Queue Musicale
const MusicQueue = ({ queue, currentTrack, onAddToQueue }) => {
  console.log('📋 Phase 4: Rendu MusicQueue', { queue, currentTrack });

  const [newTrackUrl, setNewTrackUrl] = useState('');

  const handleAddTrack = () => {
    if (newTrackUrl.trim()) {
      onAddToQueue(newTrackUrl);
      setNewTrackUrl('');
    }
  };

  return (
    <div className="music-queue">
      {/* Ajout rapide */}
      <div className="music-add-section">
        <h3>➕ Ajouter une Musique</h3>
        <div className="music-add-form">
          <input
            type="text"
            placeholder="URL YouTube, Spotify ou terme de recherche..."
            value={newTrackUrl}
            onChange={(e) => setNewTrackUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddTrack()}
            className="music-add-input"
          />
          <button 
            onClick={handleAddTrack}
            className="music-btn-primary"
            disabled={!newTrackUrl.trim()}
          >
            Ajouter
          </button>
        </div>
      </div>

      {/* Piste actuelle */}
      {currentTrack && (
        <div className="music-current-section">
          <h3>🎵 En cours de lecture</h3>
          <div className="music-queue-item current">
            <div className="music-queue-thumbnail">
              {currentTrack.thumbnail ? (
                <img src={currentTrack.thumbnail} alt={currentTrack.title} />
              ) : (
                <div className="music-queue-placeholder">🎵</div>
              )}
            </div>
            <div className="music-queue-info">
              <span className="music-queue-title">{currentTrack.title}</span>
              <span className="music-queue-artist">{currentTrack.artist || currentTrack.uploader}</span>
              <span className="music-queue-requester">Par: {currentTrack.requested_by}</span>
            </div>
            <div className="music-queue-duration">
              {Math.floor(currentTrack.duration / 60)}:{(currentTrack.duration % 60).toString().padStart(2, '0')}
            </div>
          </div>
        </div>
      )}

      {/* Queue à venir */}
      <div className="music-queue-section">
        <h3>📋 À venir ({queue.length})</h3>
        {queue.length > 0 ? (
          <div className="music-queue-list">
            {queue.map((track, index) => (
              <div key={track.id || index} className="music-queue-item">
                <span className="music-queue-position">{index + 1}</span>
                <div className="music-queue-thumbnail">
                  {track.thumbnail ? (
                    <img src={track.thumbnail} alt={track.title} />
                  ) : (
                    <div className="music-queue-placeholder">🎵</div>
                  )}
                </div>
                <div className="music-queue-info">
                  <span className="music-queue-title">{track.title}</span>
                  <span className="music-queue-artist">{track.artist || track.uploader}</span>
                  <span className="music-queue-requester">Par: {track.requested_by}</span>
                </div>
                <div className="music-queue-duration">
                  {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="music-queue-empty">
            <p>📭 La queue est vide</p>
            <p>Ajoutez des musiques pour les voir ici</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Placeholders pour les autres composants (à implémenter)
const MusicSearch = ({ onAddToQueue, serverId }) => (
  <div className="music-search">
    <h3>🔍 Recherche Musicale</h3>
    <div className="music-coming-soon">
      <p>🚧 Interface de recherche en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>🔍 Recherche YouTube, Spotify, SoundCloud</li>
        <li>🎵 Aperçu des résultats</li>
        <li>➕ Ajout direct à la queue</li>
        <li>📊 Suggestions populaires</li>
      </ul>
    </div>
  </div>
);

const MusicPlaylists = ({ serverId, onAddToQueue }) => (
  <div className="music-playlists">
    <h3>📚 Gestion des Playlists</h3>
    <div className="music-coming-soon">
      <p>🚧 Interface de playlists en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>📚 Création de playlists personnalisées</li>
        <li>💾 Sauvegarde de favoris</li>
        <li>🔄 Import/Export de playlists</li>
        <li>👥 Playlists partagées du serveur</li>
      </ul>
    </div>
  </div>
);

const MusicConfig = ({ config, onSave }) => (
  <div className="music-config">
    <h3>⚙️ Configuration Musicale</h3>
    <div className="music-coming-soon">
      <p>🚧 Interface de configuration en développement</p>
      <p>Cette section permettra :</p>
      <ul>
        <li>⚙️ Paramètres de qualité audio</li>
        <li>🔊 Contrôles de volume par défaut</li>
        <li>📋 Limites de queue</li>
        <li>🚫 Filtres de contenu</li>
        <li>👥 Permissions musicales</li>
      </ul>
    </div>
  </div>
);

export default MusicManager;
