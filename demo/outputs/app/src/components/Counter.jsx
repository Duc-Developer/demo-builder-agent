import React from "react";

export default function Counter({ remaining }) {
  return (
    <div className="small" aria-label={`Còn lại: ${remaining}`}>
      Còn lại: <strong style={{ color: "rgba(255,255,255,0.92)" }}>{remaining}</strong>
    </div>
  );
}

