import React from "react";
import "./TrackCard.css";

const GENRE_COLORS = {
  Pop: "#FF6B9D",
  Rock: "#C084FC",
  "Hip-Hop": "#FBBF24",
  "R&B": "#34D399",
  Latin: "#F97316",
  Jazz: "#60A5FA",
  Classical: "#A78BFA",
  Electronic: "#22D3EE",
  "K-Pop": "#FB7185",
  Folk: "#4ADE80",
  Country: "#D97706",
};

const getGenreColor = (genre) => GENRE_COLORS[genre] || "#94A3B8";

function TrackCard({ track, isSelected, onClick, showSimilarity }) {
  const color = getGenreColor(track.genre);

  return (
    <div
      className={`track-card ${isSelected ? "track-card--selected" : ""}`}
      style={{
        "--genre-color": color,
        borderColor: isSelected ? color : undefined,
        background: isSelected
          ? `linear-gradient(135deg, ${color}12, ${color}06)`
          : undefined,
      }}
      onClick={onClick}
    >
      <div className="track-card__header">
        <div className="track-card__info">
          <h4 className="track-card__name">{track.track_name}</h4>
          <p className="track-card__artist">
            {track.artist_name} · {track.year}
          </p>
        </div>
        <span
          className="track-card__genre"
          style={{ background: `${color}18`, color: color }}
        >
          {track.genre}
        </span>
      </div>

      {showSimilarity && track.similarity_pct !== undefined && (
        <div className="track-card__similarity">
          <div className="track-card__sim-bar">
            <div
              className="track-card__sim-fill"
              style={{
                width: `${track.similarity_pct}%`,
                background: `linear-gradient(90deg, ${color}, ${color}90)`,
              }}
            />
          </div>
          <span className="track-card__sim-value" style={{ color }}>
            {track.similarity_pct}%
          </span>
        </div>
      )}
    </div>
  );
}

export { getGenreColor };
export default TrackCard;
