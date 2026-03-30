import React, { useId } from "react";
import FilterTabs from "./controls/FilterTabs.jsx";
import SearchInput from "./controls/SearchInput.jsx";

/**
 * @param {{
 *  filter: "all" | "active" | "completed",
 *  onChangeFilter: (f: "all" | "active" | "completed") => void,
 *  searchQuery: string,
 *  onChangeSearch: (q: string) => void,
 *  completedCount: number,
 *  onClearCompleted: () => void
 * }} props
 */
export default function TodoControls({
  filter,
  onChangeFilter,
  searchQuery,
  onChangeSearch,
  completedCount,
  onClearCompleted
}) {
  const controlsLabelId = useId();

  return (
    <section className="section" aria-labelledby={controlsLabelId}>
      <div className="sectionHeader">
        <h2 id={controlsLabelId} className="sectionTitle">Bộ lọc & tìm kiếm</h2>
      </div>

      <div className="controlsGrid">
        <div className="controlsLeft">
          <FilterTabs value={filter} onChange={onChangeFilter} />
        </div>

        <div className="controlsRight">
          <SearchInput value={searchQuery} onChange={onChangeSearch} />
          <button
            type="button"
            className="btn btnGhost"
            onClick={onClearCompleted}
            disabled={completedCount === 0}
            aria-disabled={completedCount === 0 ? "true" : "false"}
            title={completedCount === 0 ? "Không có việc đã hoàn thành" : "Xóa tất cả việc đã hoàn thành"}
          >
            Xóa đã hoàn thành
          </button>
        </div>
      </div>
    </section>
  );
}

