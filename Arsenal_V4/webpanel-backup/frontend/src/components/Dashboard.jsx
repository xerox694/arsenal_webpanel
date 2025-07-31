import React from "react";
import { useApp } from "../contexts/AppContext";
import { useStats, useServers } from "../hooks/useAPI";
import "./Dashboard.css";

export default function Dashboard() {
  const { isAuthenticated, profile, permissions, navigateTo } = useApp();
  const { stats, loading: statsLoading } = useStats();
  const { servers, loading: serversLoading } = useServers();

  if (!isAuthenticated) {
    return (
      <section className="uix-dashboard">
        <div className="uix-stats-card">
          <h3>Non connecté</h3>
          <p>Veuillez vous connecter via Discord pour accéder au dashboard.</p>
          <button 
            className="uix-neon-btn"
            onClick={() => window.location.href = '/auth/discord'}
          >
            Se connecter avec Discord
          </button>
        </div>
      </section>
    );
  }

  const loading = statsLoading || serversLoading;

  return (
    <section className="uix-dashboard">
      {/* Statistiques principales */}
      <div className="uix-stats-card">
        <h3>🤖 Statistiques Arsenal V4</h3>
        {loading ? (
          <div className="uix-loading">Chargement...</div>
        ) : (
          <ul>
            <li>
              Serveurs connectés : 
              <span className="uix-neon">{stats?.servers || 0}</span>
            </li>
            <li>
              Utilisateurs actifs : 
              <span className="uix-neon">{stats?.active_users || 0}</span>
            </li>
            <li>
              Commandes exécutées : 
              <span className="uix-neon">{stats?.commands_today || 0}</span>
            </li>
            <li>
              Status bot : 
              <span className={`uix-status ${stats?.online_status ? 'online' : 'offline'}`}>
                {stats?.online_status ? '🟢 En ligne' : '🔴 Hors ligne'}
              </span>
            </li>
          </ul>
        )}
      </div>

      {/* Informations utilisateur */}
      <div className="uix-stats-card">
        <h3>👤 Profil Utilisateur</h3>
        {profile ? (
          <div className="uix-profile-info">
            <div className="uix-profile-header">
              <img 
                src={profile.avatar} 
                alt="Avatar" 
                className="uix-avatar-small"
              />
              <div>
                <strong>{profile.display_name}</strong>
                <br />
                <span className="uix-role">{profile.role_display}</span>
              </div>
            </div>
            <ul>
              <li>
                Niveau d'accès : 
                <span className="uix-neon">{profile.numeric_level}</span>
              </li>
              <li>
                Serveurs accessibles : 
                <span className="uix-neon">{profile.accessible_servers}</span>
              </li>
              <li>
                Dernière connexion : 
                <span className="uix-time">
                  {new Date(profile.last_seen).toLocaleString('fr-FR')}
                </span>
              </li>
            </ul>
          </div>
        ) : (
          <div className="uix-loading">Chargement du profil...</div>
        )}
      </div>

      {/* Actions rapides */}
      <div className="uix-stats-card">
        <h3>⚡ Actions Rapides</h3>
        <div className="uix-quick-actions">
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('servers')}
          >
            🏠 Gérer Serveurs
          </button>
          
          {permissions?.can_manage_bot && (
            <button 
              className="uix-neon-btn"
              onClick={() => navigateTo('admin')}
            >
              ⚙️ Panel Admin
            </button>
          )}
          
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('economy')}
          >
            💰 Économie
          </button>
          
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('moderation')}
          >
            🛡️ Modération
          </button>
          
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('music')}
          >
            🎵 Musique
          </button>
          
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('gaming')}
          >
            🎮 Gaming
          </button>
          
          <button 
            className="uix-neon-btn"
            onClick={() => navigateTo('analytics')}
          >
            📊 Analytics
          </button>
        </div>
      </div>

      {/* Serveurs récents */}
      {servers && servers.length > 0 && (
        <div className="uix-stats-card">
          <h3>🏆 Vos Serveurs</h3>
          <div className="uix-servers-grid">
            {servers.slice(0, 3).map(server => (
              <div 
                key={server.id} 
                className="uix-server-card"
                onClick={() => navigateTo('server', server)}
              >
                <div className="uix-server-header">
                  {server.icon ? (
                    <img src={server.icon} alt="Icon" className="uix-server-icon" />
                  ) : (
                    <div className="uix-server-icon-placeholder">
                      {server.name.charAt(0)}
                    </div>
                  )}
                  <div>
                    <strong>{server.name}</strong>
                    <br />
                    <small>{server.member_count} membres</small>
                  </div>
                </div>
                <div className="uix-server-status">
                  <span className={`uix-status ${server.online ? 'online' : 'offline'}`}>
                    {server.online ? '🟢' : '🔴'}
                  </span>
                  <span className="uix-role-small">{server.user_role}</span>
                </div>
              </div>
            ))}
          </div>
          {servers.length > 3 && (
            <button 
              className="uix-neon-btn-small"
              onClick={() => navigateTo('servers')}
            >
              Voir tous les serveurs ({servers.length})
            </button>
          )}
        </div>
      )}
    </section>
  );
}