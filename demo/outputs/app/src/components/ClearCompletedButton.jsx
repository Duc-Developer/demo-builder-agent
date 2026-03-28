import React from "react";

export default function ClearCompletedButton({ completed, onClick }) {
  if (!completed) return null;
  return (
    <button
      type="button"
      className="btn danger"
      onClick={onClick}
      aria-label="Xóa các việc đã hoàn thành"
    >
      Xóa các việc đã hoàn thành
    </button>
  );
}

