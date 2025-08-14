import React, { useState } from "react";
import "./ConsoleIA.css";

export default function ConsoleIA() {
  const [history, setHistory] = useState([
    { type: "system", text: "Bienvenue dans la Console IA ATHENA." }
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    setHistory([...history, { type: "user", text: input }]);
    // Simule une réponse IA
    setTimeout(() => {
      setHistory(h =>
        [...h, { type: "athena", text: `ATHENA répond : "${input}"` }]
      );
    }, 600);
    setInput("");
  };

  return (
    <div className="uix-console">
      <div className="uix-console-history">
        {history.map((msg, idx) => (
          <div key={idx} className={`uix-console-msg ${msg.type}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="uix-console-input">
        <input
          type="text"
          value={input}
          placeholder="Parle à ATHENA..."
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
        />
        <button className="uix-neon-btn" onClick={handleSend}>Envoyer</button>
      </div>
    </div>
  );
}