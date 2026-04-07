import React from "react";
import "./FilterPanel.css";

function FilterPanel({
  genres,
  moods,
  selectedGenre,
  selectedMood,
  onGenreChange,
  onMoodChange,
  onSubmit,
  loading,
  favMode,
  favCount,
}) {
  return (
    <div className="filter-panel">
      {favMode && favCount > 0 && (
        <div className="filter-panel__fav-info">
          Goi y dua tren {favCount} bai hat trong gio yeu thich
        </div>
      )}

      <div className="filter-panel__grid">
        <div className="filter-panel__field">
          <label className="filter-panel__label">The loai yeu thich</label>
          <select
            className="filter-panel__select"
            value={selectedGenre}
            onChange={(e) => onGenreChange(e.target.value)}
          >
            <option value="">Tat ca the loai</option>
            {genres.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-panel__field">
          <label className="filter-panel__label">Tam trang hien tai</label>
          <select
            className="filter-panel__select"
            value={selectedMood}
            onChange={(e) => onMoodChange(e.target.value)}
          >
            <option value="">Tat ca tam trang</option>
            {moods.map((m) => (
              <option key={m.key} value={m.key}>
                {m.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        className="filter-panel__submit"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? (
          <span className="filter-panel__spinner" />
        ) : (
          <>
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M9 18V5l12-2v13" />
              <circle cx="6" cy="18" r="3" />
              <circle cx="18" cy="16" r="3" />
            </svg>
            {favMode ? "Goi y tu gio yeu thich" : "Goi y nhac cho toi"}
          </>
        )}
      </button>
    </div>
  );
}

export default FilterPanel;
