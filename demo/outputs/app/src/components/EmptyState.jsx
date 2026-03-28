import React from "react";

export default function EmptyState({ text }) {
  return (
    <div className="empty" role="status" aria-live="polite">
      {text}
    </div>
  );
}