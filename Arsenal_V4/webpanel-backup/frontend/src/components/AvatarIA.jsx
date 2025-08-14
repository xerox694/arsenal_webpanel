import React from "react";
import "./AvatarIA.css";

export default function AvatarIA() {
  return (
    <div className="uix-avatar">
      <div className="uix-avatar-circle">
        {/* Remplace par une image animée ou SVG pour un effet 2500 */}
        <span className="uix-avatar-initial">A</span>
      </div>
      <div className="uix-avatar-info">
        <h4>ATHENA</h4>
        <p>IA Signature Arsenal</p>
      </div>
    </div>
  );
}