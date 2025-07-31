import React from "react";
import "./NeonCard.css";

export default function NeonCard({ children }) {
  return (
    <div className="uix-neon-card">
      {children}
    </div>
  );
}