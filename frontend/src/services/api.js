/**
 * API Service - Giao tiep voi Backend Flask API
 * Base URL co the thay doi qua bien moi truong REACT_APP_API_URL
 */

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

class ApiService {
  /**
   * Goi API chung
   */
  async _fetch(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: { "Content-Type": "application/json" },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`[API] ${endpoint} failed:`, error);
      throw error;
    }
  }

  // ===== TRACKS =====

  /** Lay danh sach bai hat (co the tim kiem) */
  async getTracks(query = "", limit = 20) {
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (limit) params.set("limit", limit);
    return this._fetch(`/tracks?${params.toString()}`);
  }

  /** Lay chi tiet 1 bai hat */
  async getTrackDetail(trackId) {
    return this._fetch(`/tracks/${trackId}`);
  }

  // ===== FILTERS =====

  /** Lay danh sach the loai */
  async getGenres() {
    return this._fetch("/genres");
  }

  /** Lay danh sach tam trang */
  async getMoods() {
    return this._fetch("/moods");
  }

  // ===== RECOMMENDATION =====

  /** Goi y nhac tu 1 bai hat */
  async recommend(trackId, genre = null, mood = null, topN = 10) {
    return this._fetch("/recommend", {
      method: "POST",
      body: JSON.stringify({
        track_id: trackId,
        genre: genre,
        mood: mood,
        top_n: topN,
      }),
    });
  }

  /** Goi y nhac tu nhieu bai hat (batch) */
  async recommendBatch(trackIds, genre = null, mood = null, topN = 10) {
    return this._fetch("/recommend/batch", {
      method: "POST",
      body: JSON.stringify({
        track_ids: trackIds,
        genre: genre,
        mood: mood,
        top_n: topN,
      }),
    });
  }

  // ===== STATS =====

  /** Thong ke dataset */
  async getStats() {
    return this._fetch("/stats");
  }

  /** Health check */
  async healthCheck() {
    return this._fetch("/health");
  }
}

const apiService = new ApiService();
export default apiService;
