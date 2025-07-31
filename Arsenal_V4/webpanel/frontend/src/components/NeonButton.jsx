import React from "react";
import "./NeonButton.css";

export default function NeonButton({ children, ...props }) {
  return (
    <button className="uix-neon-btn" {...props}>
      {children}
    </button>
  );
}