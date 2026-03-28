import React from "react";
import { FILTERS } from "../todo/constants.js";

export default function FilterTabs({ value, onChange }) {
  return (
    <div className="tabs" role="tablist" aria-label="Bộ lọc trạng thái">
      <button
        type="button"
        className="tab"
        role="tab"
        aria-selected={value === FILTERS.all}
        onClick={() => onChange(FILTERS.all)}
      >
        Tất cả
      </button>
      <button
        type="button"
        className="tab"
        role="tab"
        aria-selected={value === FILTERS.active}
        onClick={() => onChange(FILTERS.active)}
      >
        Đang làm
      </button>
      <button
        type="button"
        className="tab"
        role="tab"
        aria-selected={value === FILTERS.completed}
        onClick={() => onChange(FILTERS.completed)}
      >
        Đã xong
      </button>
    </div>
  );
}

