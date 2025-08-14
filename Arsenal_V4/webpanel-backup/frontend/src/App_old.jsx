import React from "react";
import "./styles/main.css";
import Sidebar from "./components/Sidebar";
import Dashboard from "./components/Dashboard";
import ConsoleIA from "./components/ConsoleIA";
import Settings from "./components/Settings";
import AvatarIA from "./components/AvatarIA";
import Notifications from "./components/Notifications";
import Badges from "./components/Badges";
import Leaderboard from "./components/Leaderboard";
import Footer from "./components/Footer";
import NeonButton from "./NeonButton";
import NeonCard from "./NeonCard";

function App() {
  return (
    <div className="uix-bg">
      <Sidebar />
      <Notifications />
      <AvatarIA />
      <header className="uix-header">
        <h1 className="uix-title">ATHENA PANEL – UIX 2500</h1>
        <p className="uix-subtitle">L’interface du futur, immersive et personnalisable</p>
      </header>
      <main className="uix-main">
        <Dashboard />
        <ConsoleIA />
        <Settings />
        <Badges />
        <Leaderboard />
        <NeonCard>
          <h2>Bienvenue dans ATHENA</h2>
          <p>Tout est prêt pour coder le futur.</p>
          <NeonButton onClick={() => alert('Action Futuriste!')}>Action Futuriste</NeonButton>
        </NeonCard>
      </main>
      <Footer />
    </div>
  );
}

export default App;
