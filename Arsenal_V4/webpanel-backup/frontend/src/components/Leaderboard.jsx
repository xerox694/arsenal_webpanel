import React from "react";
import "./Leaderboard.css";

const leaderboard = [
  { name: "XeRoX", score: 1200, badge: "👑" },
  { name: "AthenaDev", score: 950, badge: "💻" },
  { name: "BetaTest", score: 800, badge: "🧪" },
  { name: "EliteUser", score: 700, badge: "⭐" }
];

export default function Leaderboard() {
  return (
    <div className="uix-leaderboard">
      <h4>Leaderboard ATHENA</h4>
      <table>
        <thead>
          <tr>
            <th>Badge</th>
            <th>Nom</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((user, idx) => (
            <tr key={idx}>
              <td>{user.badge}</td>
              <td>{user.name}</td>
              <td className="uix-score">{user.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}