import React, { useState } from "react";
import "./Notifications.css";

export default function Notifications() {
  const [notifs, setNotifs] = useState([
    { type: "info", text: "Panel ATHENA lancé avec succès." },
    { type: "success", text: "Connexion au bot établie." }
  ]);

  return (
    <div className="uix-notifications">
      {notifs.map((notif, idx) => (
        <div key={idx} className={`uix-notif ${notif.type}`}>
          {notif.text}
        </div>
      ))}
    </div>
  );
}