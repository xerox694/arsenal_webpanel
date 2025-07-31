import React from "react";
import { useApp } from "../contexts/AppContext";
import "./Badges.css";

export default function Badges() {
  const { isAuthenticated, getUserBadges, profile } = useApp();

  if (!isAuthenticated) {
    return (
      <div className="uix-badges">
        <h4>🏆 Badges Arsenal V4</h4>
        <div className="uix-badges-message">
          <p>Connectez-vous pour voir vos badges</p>
        </div>
      </div>
    );
  }

  const userBadges = getUserBadges();

  return (
    <div className="uix-badges">
      <h4>🏆 Badges Arsenal V4</h4>
      
      {userBadges.length > 0 ? (
        <div className="uix-badges-list">
          {userBadges.map((badge, idx) => (
            <span
              key={idx}
              className="uix-badge"
              style={{
                borderColor: badge.color,
                color: badge.color,
                boxShadow: `0 0 10px ${badge.color}40`
              }}
              title={`${badge.name} - Priority: ${badge.priority}`}
            >
              {badge.icon} {badge.name}
            </span>
          ))}
        </div>
      ) : (
        <div className="uix-badges-message">
          <p>Aucun badge obtenu pour le moment</p>
          <small>Participez aux activités pour débloquer des badges !</small>
        </div>
      )}

      {/* Statistiques de badges */}
      {profile && (
        <div className="uix-badges-stats">
          <div className="uix-badge-stat">
            <span className="uix-stat-label">Niveau d'accès :</span>
            <span className="uix-stat-value">{profile.numeric_level}</span>
          </div>
          <div className="uix-badge-stat">
            <span className="uix-stat-label">Rôle principal :</span>
            <span className="uix-stat-value">{profile.role_display}</span>
          </div>
          <div className="uix-badge-stat">
            <span className="uix-stat-label">Badges actifs :</span>
            <span className="uix-stat-value">{userBadges.length}</span>
          </div>
        </div>
      )}

      {/* Section progression (pour futures fonctionnalités) */}
      <div className="uix-badges-progress">
        <h5>🎯 Objectifs</h5>
        <div className="uix-objective">
          <span className="uix-objective-name">
            {userBadges.length < 3 ? "Débloquer 3 badges" : "Expert confirmé !"}
          </span>
          <div className="uix-progress-bar">
            <div 
              className="uix-progress-fill" 
              style={{ width: `${Math.min(100, (userBadges.length / 3) * 100)}%` }}
            ></div>
          </div>
          <span className="uix-progress-text">
            {userBadges.length}/3
          </span>
        </div>
      </div>
    </div>
  );
}