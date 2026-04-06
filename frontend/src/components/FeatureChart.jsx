import React from "react";
import "./FeatureChart.css";

const FEATURE_LABELS = {
  danceability: "Danceability",
  energy: "Energy",
  valence: "Valence",
  tempo: "Tempo",
  acousticness: "Acousticness",
  instrumentalness: "Instrumentalness",
  liveness: "Liveness",
  speechiness: "Speechiness",
};

const FEATURE_DESCRIPTIONS = {
  danceability: "Muc do phu hop de nhay",
  energy: "Cuong do & hoat dong",
  valence: "Cam xuc tich cuc",
  tempo: "Nhip do (BPM)",
  acousticness: "Muc do acoustic",
  instrumentalness: "Khong co giong hat",
  liveness: "Trinh dien truc tiep",
  speechiness: "Loi noi / rap",
};

function FeatureChart({ features, color = "#818CF8" }) {
  if (!features) return null;

  return (
    <div className="feature-chart">
      <h4 className="feature-chart__title">Dac trung am nhac</h4>
      <div className="feature-chart__list">
        {Object.entries(FEATURE_LABELS).map(([key, label]) => {
          const raw = features[key] ?? 0;
          // Tempo can chuan hoa ve 0-1 (gia su max 200 BPM)
          const value = key === "tempo" ? raw / 200 : raw;

          return (
            <div className="feature-chart__row" key={key}>
              <div className="feature-chart__label-wrap">
                <span className="feature-chart__label">{label}</span>
                <span className="feature-chart__desc">
                  {FEATURE_DESCRIPTIONS[key]}
                </span>
              </div>
              <div className="feature-chart__bar-container">
                <div className="feature-chart__bar-bg">
                  <div
                    className="feature-chart__bar-fill"
                    style={{
                      width: `${Math.min(value * 100, 100)}%`,
                      background: `linear-gradient(90deg, ${color}, ${color}80)`,
                    }}
                  />
                </div>
                <span className="feature-chart__value" style={{ color }}>
                  {key === "tempo"
                    ? `${Math.round(raw)}`
                    : `${(raw * 100).toFixed(0)}%`}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default FeatureChart;
