import React from "react";

export default function SearchBox({ value, onChange }) {
  return (
    <div className="search" aria-label="Tìm kiếm">
      <input
        className="input"
        type="text"
        placeholder="Tìm kiếm…"
        aria-label="Tìm kiếm công việc"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value ? (
        <button type="button" className="clear-x" aria-label="Xóa tìm kiếm" onClick={() => onChange("")}>
          ×
        </button>
      ) : null}
    </div>
  );
}

