import React from "react";
import { AppProvider, useApp } from "./contexts/AppContext";
import "./styles/main.css";

// Composants
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import Settings from "./components/Settings";
import Badges from "./components/Badges";
import Leaderboard from "./components/Leaderboard";
import Notifications from "./components/Notifications";
import Footer from "./components/Footer";
import EconomyManager from "./components/EconomyManager";
import ModerationManager from "./components/ModerationManager";
import MusicManager from "./components/MusicManager";
import GamingManager from "./components/GamingManager";
import AnalyticsManager from "./components/AnalyticsManager";

// Composant de routage principal
function AppContent() {
  const { currentView, isLoading, isAuthenticated } = useApp();

  // Affichage de chargement
  if (isLoading) {
    return (
      <div className="uix-bg">
        <div className="uix-loading-screen">
          <div className="uix-loader">
            <div className="uix-spinner"></div>
            <h2>Arsenal V4 WebPanel</h2>
            <p>Chargement en cours...</p>
          </div>
        </div>
      </div>
    );
  }

  // Rendu des vues selon la navigation
  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <>
            <Dashboard />
            <div className="uix-secondary-content">
              <Badges />
              <Leaderboard />
            </div>
          </>
        );
      
      case 'servers':
        return (
          <div className="uix-content-full">
            <h2>🏠 Gestion des Serveurs</h2>
            <p>Interface de gestion des serveurs en développement...</p>
            {/* TODO: Composant ServersManager */}
          </div>
        );
      
      case 'economy':
        console.log('🚀 Phase 2: Rendu EconomyManager');
        return <EconomyManager />;
      
      case 'moderation':
        console.log('🛡️ Phase 3: Rendu ModerationManager');
        return <ModerationManager />;
      
      case 'music':
        console.log('🎵 Phase 4: Rendu MusicManager');
        return <MusicManager />;
      
      case 'gaming':
        console.log('🎮 Phase 5: Rendu GamingManager');
        return <GamingManager />;
      
      case 'moderation':
        return <ModerationManager />;
      
      case 'music':
        return <MusicManager />;
        
      case 'gaming':
        return <GamingManager />;
        
      case 'analytics':
        return <AnalyticsManager />;
      
      case 'admin':
        return (
          <div className="uix-content-full">
            <h2>⚙️ Panel Administrateur</h2>
            <p>Interface d'administration en développement...</p>
            {/* TODO: Composant AdminPanel */}
          </div>
        );
      
      case 'founder':
        return (
          <div className="uix-content-full">
            <h2>👑 Founder Panel</h2>
            <p>Outils de fondateur en développement...</p>
            {/* TODO: Composant FounderPanel */}
          </div>
        );
      
      case 'creator':
        return (
          <div className="uix-content-full">
            <h2>🔧 Creator Tools</h2>
            <p>Outils de créateur en développement...</p>
            {/* TODO: Composant CreatorTools */}
          </div>
        );
      
      case 'settings':
        return <Settings />;
      
      default:
        return (
          <>
            <Dashboard />
            <div className="uix-secondary-content">
              <Badges />
              <Leaderboard />
            </div>
          </>
        );
    }
  };

  return (
    <div className="uix-bg">
      <Sidebar />
      <Notifications />
      
      <header className="uix-header">
        <h1 className="uix-title">
          🤖 Arsenal V4 – WebPanel Advanced
        </h1>
        <p className="uix-subtitle">
          {isAuthenticated 
            ? "Interface de gestion avancée pour votre bot Discord" 
            : "Connectez-vous pour accéder au panel de contrôle"
          }
        </p>
      </header>
      
      <main className="uix-main">
        {renderCurrentView()}
      </main>
      
      <Footer />
    </div>
  );
}

// App principal avec Provider
function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
