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
        return (
          <div className="uix-content-full">
            <h2>💰 Système Économique</h2>
            <p>Interface économique en développement...</p>
            {/* TODO: Composant EconomyManager */}
          </div>
        );
      
      case 'music':
        return (
          <div className="uix-content-full">
            <h2>🎵 Système Musical</h2>
            <p>Interface musicale en développement...</p>
            {/* TODO: Composant MusicManager */}
          </div>
        );
      
      case 'moderation':
        return (
          <div className="uix-content-full">
            <h2>🛡️ Modération</h2>
            <p>Outils de modération en développement...</p>
            {/* TODO: Composant ModerationTools */}
          </div>
        );
      
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
