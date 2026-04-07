import React, { useState, useEffect, useCallback, useRef } from "react";
import apiService from "./services/api";
import SearchBar from "./components/SearchBar";
import StepIndicator from "./components/StepIndicator";
import TrackCard from "./components/TrackCard";
import { getGenreColor } from "./components/TrackCard";
import FilterPanel from "./components/FilterPanel";
import FeatureChart from "./components/FeatureChart";
import "./App.css";

function App() {
  // ===== State =====
  const [step, setStep] = useState(1);
  const [search, setSearch] = useState("");
  const [tracks, setTracks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [moods, setMoods] = useState([]);
  const [stats, setStats] = useState(null);

  const [selectedTrack, setSelectedTrack] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState("");
  const [selectedMood, setSelectedMood] = useState("");

  const [recommendations, setRecommendations] = useState([]);
  const [detailTrack, setDetailTrack] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTracks, setTotalTracks] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);

  // Favorites (gio bai hat yeu thich) - dung cho /api/recommend/batch
  const [favorites, setFavorites] = useState([]);
  const [favMode, setFavMode] = useState(false);

  // AbortController ref de huy request search cu
  const searchAbortRef = useRef(null);

  const PER_PAGE = 20;

  // ===== Load initial data =====
  useEffect(() => {
    const loadInitial = async () => {
      try {
        const [tracksRes, genresRes, moodsRes, statsRes] = await Promise.all([
          apiService.getTracks("", 1, PER_PAGE),
          apiService.getGenres(),
          apiService.getMoods(),
          apiService.getStats(),
        ]);
        setTracks(tracksRes.data);
        setPage(tracksRes.page);
        setTotalPages(tracksRes.total_pages);
        setTotalTracks(tracksRes.total);
        setGenres(genresRes.data);
        setMoods(moodsRes.data);
        setStats(statsRes.data);
      } catch (err) {
        setError("Khong the ket noi den server. Hay dam bao backend dang chay tai http://localhost:5000");
        console.error(err);
      }
    };
    loadInitial();
  }, []);

  // ===== Search tracks (voi AbortController fix race condition) =====
  useEffect(() => {
    const timer = setTimeout(async () => {
      // Huy request truoc do neu con dang chay
      if (searchAbortRef.current) {
        searchAbortRef.current.abort();
      }

      const controller = new AbortController();
      searchAbortRef.current = controller;

      try {
        const res = await apiService.getTracks(search, 1, PER_PAGE, controller.signal);
        setTracks(res.data);
        setPage(res.page);
        setTotalPages(res.total_pages);
        setTotalTracks(res.total);
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error("Search failed:", err);
        }
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // ===== Load More (trang tiep theo) =====
  const handleLoadMore = useCallback(async () => {
    if (page >= totalPages || loadingMore) return;
    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const res = await apiService.getTracks(search, nextPage, PER_PAGE);
      setTracks((prev) => [...prev, ...res.data]);
      setPage(res.page);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error("Load more failed:", err);
    } finally {
      setLoadingMore(false);
    }
  }, [page, totalPages, loadingMore, search]);

  // ===== Select track =====
  const handleSelectTrack = useCallback((track) => {
    setSelectedTrack(track);
    setStep(2);
  }, []);

  // ===== Toggle Favorite =====
  const handleToggleFavorite = useCallback((track, e) => {
    e.stopPropagation();
    setFavorites((prev) => {
      const exists = prev.find((f) => f.id === track.id);
      if (exists) {
        return prev.filter((f) => f.id !== track.id);
      }
      return [...prev, track];
    });
  }, []);

  // ===== Get recommendations =====
  const handleRecommend = useCallback(async () => {
    if (!favMode && !selectedTrack) return;
    if (favMode && favorites.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      let res;
      if (favMode && favorites.length > 0) {
        // Dung batch API cho gio yeu thich
        res = await apiService.recommendBatch(
          favorites.map((f) => f.id),
          selectedGenre || null,
          selectedMood || null,
          10
        );
      } else {
        res = await apiService.recommend(
          selectedTrack.id,
          selectedGenre || null,
          selectedMood || null,
          10
        );
      }
      setRecommendations(res.data.recommendations);
      setStep(3);
    } catch (err) {
      setError("Loi khi goi y nhac. Vui long thu lai.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedTrack, selectedGenre, selectedMood, favMode, favorites]);

  // ===== View track detail =====
  const handleViewDetail = useCallback(
    (track) => {
      setDetailTrack(detailTrack?.id === track.id ? null : track);
    },
    [detailTrack]
  );

  // ===== Reset =====
  const handleReset = useCallback(() => {
    setStep(1);
    setSelectedTrack(null);
    setSelectedGenre("");
    setSelectedMood("");
    setRecommendations([]);
    setDetailTrack(null);
    setSearch("");
    setFavMode(false);
  }, []);

  // ===== Toggle fav mode =====
  const handleToggleFavMode = useCallback(() => {
    setFavMode((prev) => !prev);
    if (!favMode) {
      // Khi bat fav mode, neu co favorites thi chuyen sang step 2
      setSelectedTrack(null);
      if (favorites.length > 0) {
        setStep(2);
      }
    }
  }, [favMode, favorites]);

  return (
    <div className="app">
      {/* ===== HEADER ===== */}
      <header className="app__header">
        <div className="app__header-inner">
          <h1 className="app__title" onClick={handleReset}>
            Music Recommendation System
          </h1>
          <p className="app__subtitle">
            He thong goi y nhac dua tren thong tin ca nhan — Content-based
            Filtering + Cosine Similarity
          </p>
          {stats && (
            <div className="app__stats">
              <span>{stats.total_tracks} bai hat</span>
              <span className="app__stats-dot">·</span>
              <span>{stats.total_artists} nghe si</span>
              <span className="app__stats-dot">·</span>
              <span>{stats.total_genres} the loai</span>
            </div>
          )}
          <StepIndicator currentStep={step} onStepClick={setStep} />
        </div>
      </header>

      {/* ===== MAIN CONTENT ===== */}
      <main className="app__main">
        {error && (
          <div className="app__error">
            <span>!</span> {error}
          </div>
        )}

        {/* ----- FAVORITES BAR ----- */}
        {favorites.length > 0 && step < 3 && (
          <div className="app__favorites-bar">
            <div className="app__favorites-header">
              <span className="app__favorites-label">
                Gio yeu thich ({favorites.length})
              </span>
              <button
                className={`app__fav-mode-btn ${favMode ? "app__fav-mode-btn--active" : ""}`}
                onClick={handleToggleFavMode}
              >
                {favMode ? "Dang dung gio yeu thich" : "Goi y tu gio yeu thich"}
              </button>
            </div>
            <div className="app__favorites-list">
              {favorites.map((f) => (
                <span key={f.id} className="app__fav-chip">
                  {f.track_name}
                  <button
                    className="app__fav-chip-remove"
                    onClick={(e) => handleToggleFavorite(f, e)}
                  >
                    x
                  </button>
                </span>
              ))}
            </div>
            {favMode && favorites.length > 0 && step < 2 && (
              <button
                className="app__fav-proceed-btn"
                onClick={() => setStep(2)}
              >
                Tiep tuc chon bo loc
              </button>
            )}
          </div>
        )}

        {/* ----- STEP 1: Chon bai hat ----- */}
        {step >= 1 && (
          <section className="app__section">
            <h3 className="app__section-title">
              <span className="app__section-num">1</span>
              Chon bai hat ban yeu thich
            </h3>

            <SearchBar
              value={search}
              onChange={setSearch}
              placeholder="Tim kiem bai hat hoac nghe si..."
            />

            <div
              className="app__track-grid"
              style={{ maxHeight: step === 1 ? 460 : 220 }}
            >
              {tracks.map((t) => (
                <TrackCard
                  key={t.id}
                  track={t}
                  isSelected={selectedTrack?.id === t.id}
                  isFavorited={favorites.some((f) => f.id === t.id)}
                  onClick={() => handleSelectTrack(t)}
                  onFavorite={(e) => handleToggleFavorite(t, e)}
                  showSimilarity={false}
                />
              ))}
              {tracks.length === 0 && (
                <p className="app__empty">
                  Khong tim thay bai hat nao.
                </p>
              )}
            </div>

            {/* Load More button */}
            {page < totalPages && (
              <div className="app__load-more">
                <button
                  className="app__load-more-btn"
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                >
                  {loadingMore
                    ? "Dang tai..."
                    : `Tai them (${tracks.length}/${totalTracks})`}
                </button>
              </div>
            )}

            {selectedTrack && !favMode && (
              <div className="app__selected-banner">
                <span className="app__selected-label">Da chon:</span>
                <strong>{selectedTrack.track_name}</strong>
                <span className="app__selected-sep">—</span>
                <span>{selectedTrack.artist_name}</span>
                <span
                  className="app__selected-genre"
                  style={{
                    background: `${getGenreColor(selectedTrack.genre)}20`,
                    color: getGenreColor(selectedTrack.genre),
                  }}
                >
                  {selectedTrack.genre}
                </span>
              </div>
            )}
          </section>
        )}

        {/* ----- STEP 2: Bo loc ----- */}
        {step >= 2 && (
          <section className="app__section">
            <h3 className="app__section-title">
              <span className="app__section-num">2</span>
              Thong tin ca nhan &amp; Bo loc
            </h3>
            <FilterPanel
              genres={genres}
              moods={moods}
              selectedGenre={selectedGenre}
              selectedMood={selectedMood}
              onGenreChange={setSelectedGenre}
              onMoodChange={setSelectedMood}
              onSubmit={handleRecommend}
              loading={loading}
              favMode={favMode}
              favCount={favorites.length}
            />
          </section>
        )}

        {/* ----- STEP 3: Ket qua ----- */}
        {step === 3 && (
          <section className="app__section">
            <div className="app__results-header">
              <h3 className="app__section-title" style={{ marginBottom: 0 }}>
                <span className="app__section-num">3</span>
                Ket qua goi y ({recommendations.length} bai hat)
                {favMode && (
                  <span className="app__results-badge">Tu gio yeu thich</span>
                )}
              </h3>
              <button className="app__reset-btn" onClick={handleReset}>
                Lam lai
              </button>
            </div>

            {recommendations.length > 0 ? (
              <>
                <div className="app__track-grid app__track-grid--results">
                  {recommendations.map((t) => (
                    <TrackCard
                      key={t.id}
                      track={t}
                      isSelected={detailTrack?.id === t.id}
                      isFavorited={favorites.some((f) => f.id === t.id)}
                      onClick={() => handleViewDetail(t)}
                      onFavorite={(e) => handleToggleFavorite(t, e)}
                      showSimilarity={true}
                    />
                  ))}
                </div>

                {detailTrack && (
                  <div
                    className="app__detail"
                    style={{
                      borderColor: `${getGenreColor(detailTrack.genre)}40`,
                    }}
                  >
                    <div className="app__detail-header">
                      <div>
                        <h3 className="app__detail-name">
                          {detailTrack.track_name}
                        </h3>
                        <p className="app__detail-meta">
                          {detailTrack.artist_name} · {detailTrack.genre} ·{" "}
                          {detailTrack.year}
                        </p>
                      </div>
                      <div
                        className="app__detail-score"
                        style={{ color: getGenreColor(detailTrack.genre) }}
                      >
                        {detailTrack.similarity_pct}%
                      </div>
                    </div>
                    <FeatureChart
                      features={{
                        danceability: detailTrack.danceability,
                        energy: detailTrack.energy,
                        valence: detailTrack.valence,
                        tempo: detailTrack.tempo,
                        acousticness: detailTrack.acousticness,
                        instrumentalness: detailTrack.instrumentalness,
                        liveness: detailTrack.liveness,
                        speechiness: detailTrack.speechiness,
                      }}
                      color={getGenreColor(detailTrack.genre)}
                    />
                  </div>
                )}
              </>
            ) : (
              <div className="app__empty-results">
                <div className="app__empty-icon">:/</div>
                <p>Khong tim thay bai hat phu hop. Thu thay doi bo loc.</p>
              </div>
            )}
          </section>
        )}

        {/* ===== ALGORITHM INFO ===== */}
        <section className="app__algo-info">
          <h4 className="app__algo-title">
            Thuat toan Content-based Filtering
          </h4>
          <p className="app__algo-text">
            He thong su dung 8 dac trung am nhac (danceability, energy, valence,
            tempo, acousticness, instrumentalness, liveness, speechiness) de
            bieu dien moi bai hat duoi dang vector. Sau khi chuan hoa bang
            MinMaxScaler, he thong tinh Cosine Similarity on-the-fly giua bai
            hat ban chon va tat ca bai hat con lai, sau do sap xep theo do tuong
            dong giam dan va tra ve top-10 ket qua. Mood filters duoc tinh
            tu percentile du lieu thuc te. Ket qua duoc da dang hoa bang
            randomness cho cac bai hat co diem tuong dong xap xi.
          </p>
          <p className="app__algo-footer">
            Backend: Python Flask + Scikit-learn · Frontend: React.js · Dataset:
            Spotify audio features
          </p>
        </section>
      </main>
    </div>
  );
}

export default App;
