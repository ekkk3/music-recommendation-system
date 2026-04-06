import React from "react";
import "./SearchBar.css";

function SearchBar({ value, onChange, placeholder }) {
  return (
    <div className="search-bar">
      <svg
        className="search-bar__icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
      <input
        className="search-bar__input"
        type="text"
        placeholder={placeholder || "Tim kiem..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value && (
        <button className="search-bar__clear" onClick={() => onChange("")}>
          ✕
        </button>
      )}
    </div>
  );
}

export default SearchBar;
