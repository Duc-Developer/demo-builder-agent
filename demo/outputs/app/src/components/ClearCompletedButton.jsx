import React from "react";

export default function ClearCompletedButton({ completed, onClick }) {
  if (!completed) return null;
  return (
    <button type="button" className="btn danger" onClick={onClick} aria-label="Xóa việc đã xong">
      Xóa việc đã xong
    </button>
  );
}

