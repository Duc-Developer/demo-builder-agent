import React from "react";
import FilterTabs from "./FilterTabs.jsx";
import SearchBox from "./SearchBox.jsx";
import Counter from "./Counter.jsx";
import ClearCompletedButton from "./ClearCompletedButton.jsx";

export default function TodoControls({
  filter,
  onChangeFilter,
  searchQuery,
  onChangeSearch,
  remaining,
  completed,
  onClearCompleted,
}) {
  return (
    <div className="controls" aria-label="Thanh điều khiển">
      <div className="controls-left">
        <FilterTabs value={filter} onChange={onChangeFilter} />
        <SearchBox value={searchQuery} onChange={onChangeSearch} />
      </div>

      <div className="controls-left" style={{ justifyContent: "flex-end" }}>
        <Counter remaining={remaining} />
        <ClearCompletedButton completed={completed} onClick={onClearCompleted} />
      </div>
    </div>
  );
}

