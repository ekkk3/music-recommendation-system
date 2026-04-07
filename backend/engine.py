"""
Music Recommendation Engine
Phuong phap: Content-based Filtering + Cosine Similarity

Cai tien:
- Tinh Cosine Similarity on-the-fly (khong luu ma tran NxN) de ho tro dataset lon
- Mood filters dua tren percentile cua du lieu thuc te
- Them yeu to ngau nhien (randomness) de da dang hoa goi y
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os
import random

# ============================================================
# Cac dac trung am nhac su dung de tinh toan do tuong dong
# ============================================================
AUDIO_FEATURES = [
    "danceability", "energy", "valence", "tempo",
    "acousticness", "instrumentalness", "liveness", "speechiness"
]

# ============================================================
# Dinh nghia cac tam trang (mood) voi percentile range
# Thay vi hardcode nguong co dinh, dung percentile de tu dong
# thich nghi voi phan bo du lieu thuc te
# ============================================================
MOOD_DEFINITIONS = {
    "happy": {
        "label": "Vui ve / Nang luong",
        "percentile_conditions": {
            "valence": {"min_pct": 65, "max_pct": 100},
            "energy": {"min_pct": 60, "max_pct": 100}
        }
    },
    "sad": {
        "label": "Buon / Tram lang",
        "percentile_conditions": {
            "valence": {"min_pct": 0, "max_pct": 35},
            "energy": {"min_pct": 0, "max_pct": 40}
        }
    },
    "relax": {
        "label": "Thu gian / Binh yen",
        "percentile_conditions": {
            "energy": {"min_pct": 0, "max_pct": 40},
            "acousticness": {"min_pct": 50, "max_pct": 100}
        }
    },
    "party": {
        "label": "Soi dong / Party",
        "percentile_conditions": {
            "danceability": {"min_pct": 65, "max_pct": 100},
            "energy": {"min_pct": 60, "max_pct": 100}
        }
    },
    "focus": {
        "label": "Tap trung / Lam viec",
        "percentile_conditions": {
            "instrumentalness": {"min_pct": 30, "max_pct": 100},
            "energy": {"min_pct": 20, "max_pct": 60}
        }
    },
}

# Nguong de coi 2 bai hat la "xap xi nhau" ve similarity
SIMILARITY_JITTER_THRESHOLD = 0.02


class RecommendationEngine:
    """
    Content-based Music Recommendation Engine

    Pipeline:
    1. Load dataset tu CSV
    2. Chuan hoa features bang MinMaxScaler
    3. Tinh Mood filters dua tren percentile cua du lieu
    4. Khi nguoi dung chon bai hat -> tinh Cosine Similarity on-the-fly
       va tra ve top-N bai hat tuong tu nhat (co randomness)
    """

    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), "data", "tracks.csv")

        self.data_path = data_path
        self.df = None
        self.scaler = MinMaxScaler()
        self.feature_matrix = None
        self.mood_filters = {}
        self._load_and_process()

    def _load_and_process(self):
        """Buoc 1-3: Load, chuan hoa, tinh mood thresholds"""
        # Buoc 1: Load dataset
        self.df = pd.read_csv(self.data_path)
        self.df = self.df.dropna(subset=AUDIO_FEATURES)
        self.df = self.df.drop_duplicates(subset=["track_name", "artist_name"])
        self.df = self.df.reset_index(drop=True)

        # Buoc 2: Chuan hoa features ve [0, 1]
        self.feature_matrix = self.scaler.fit_transform(self.df[AUDIO_FEATURES])

        # Buoc 3: Tinh mood filters dua tren percentile cua du lieu thuc te
        self._compute_mood_filters()

        print(f"[Engine] Loaded {len(self.df)} tracks, feature matrix: {self.feature_matrix.shape}")
        print(f"[Engine] Mood filters computed from data percentiles (no precomputed NxN matrix)")

    def _compute_mood_filters(self):
        """Tinh nguong mood tu percentile cua du lieu thuc te"""
        for mood_key, mood_def in MOOD_DEFINITIONS.items():
            conditions = {}
            for feature, pct_range in mood_def["percentile_conditions"].items():
                lo = np.percentile(self.df[feature].values, pct_range["min_pct"])
                hi = np.percentile(self.df[feature].values, pct_range["max_pct"])
                conditions[feature] = (round(float(lo), 4), round(float(hi), 4))
            self.mood_filters[mood_key] = {
                "label": mood_def["label"],
                "conditions": conditions
            }
        print(f"[Engine] Mood thresholds: { {k: v['conditions'] for k, v in self.mood_filters.items()} }")

    def _compute_similarity_for_track(self, idx: int) -> np.ndarray:
        """
        Tinh Cosine Similarity on-the-fly cho 1 bai hat voi tat ca bai hat khac.
        Thay vi luu ma tran NxN (O(N^2) RAM), chi tinh 1 vector (O(N) RAM).
        """
        track_vector = self.feature_matrix[idx].reshape(1, -1)
        return cosine_similarity(track_vector, self.feature_matrix)[0]

    def get_all_tracks(self, page: int = 1, per_page: int = 20) -> dict:
        """
        Tra ve danh sach bai hat co phan trang

        Returns:
            dict voi keys: tracks, total, page, per_page, total_pages
        """
        total = len(self.df)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page

        return {
            "tracks": self.df.iloc[start:end].to_dict(orient="records"),
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }

    def get_genres(self) -> list:
        """Tra ve danh sach cac the loai nhac"""
        return sorted(self.df["genre"].unique().tolist())

    def get_moods(self) -> list:
        """Tra ve danh sach cac mood"""
        return [{"key": k, "label": v["label"]} for k, v in self.mood_filters.items()]

    def get_track_by_id(self, track_id: int) -> dict | None:
        """Tim bai hat theo ID"""
        row = self.df[self.df["id"] == track_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def search_tracks(self, query: str, page: int = 1, per_page: int = 20) -> dict:
        """
        Tim kiem bai hat theo ten hoac nghe si (co phan trang)

        Returns:
            dict voi keys: tracks, total, page, per_page, total_pages
        """
        q = query.lower().strip()
        if not q:
            return self.get_all_tracks(page=page, per_page=per_page)

        mask = (
            self.df["track_name"].str.lower().str.contains(q, na=False) |
            self.df["artist_name"].str.lower().str.contains(q, na=False)
        )
        filtered = self.df[mask]
        total = len(filtered)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page

        return {
            "tracks": filtered.iloc[start:end].to_dict(orient="records"),
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }

    def recommend(
        self,
        track_id: int,
        genre: str = None,
        mood: str = None,
        top_n: int = 10
    ) -> list:
        """
        Buoc 4: Goi y nhac (on-the-fly similarity + randomness)

        Parameters:
            track_id: ID cua bai hat nguoi dung chon
            genre: Loc theo the loai (optional)
            mood: Loc theo tam trang (optional)
            top_n: So luong bai hat goi y

        Returns:
            List cac bai hat goi y kem do tuong dong (similarity %)
        """
        # Tim index cua bai hat trong DataFrame
        idx_arr = self.df.index[self.df["id"] == track_id]
        if len(idx_arr) == 0:
            return []
        idx = idx_arr[0]

        # Tinh Cosine Similarity on-the-fly (chi 1 vector, khong luu NxN)
        sim_vector = self._compute_similarity_for_track(idx)

        # Tao danh sach (index, similarity), loai bo chinh bai hat do
        sim_scores = [(i, sim_vector[i]) for i in range(len(self.df)) if i != idx]

        # Loc theo genre
        if genre and genre.lower() not in ("all", "tat ca", ""):
            valid_indices = set(self.df.index[self.df["genre"] == genre])
            sim_scores = [(i, s) for i, s in sim_scores if i in valid_indices]

        # Loc theo mood (dung percentile-based thresholds)
        if mood and mood.lower() not in ("all", "tat ca", ""):
            mood_config = self.mood_filters.get(mood)
            if mood_config:
                conditions = mood_config["conditions"]
                valid_indices = set()
                for i in range(len(self.df)):
                    row = self.df.iloc[i]
                    match = all(
                        lo <= row[feat] <= hi
                        for feat, (lo, hi) in conditions.items()
                    )
                    if match:
                        valid_indices.add(i)
                sim_scores = [(i, s) for i, s in sim_scores if i in valid_indices]

        # Sap xep theo similarity giam dan
        sim_scores.sort(key=lambda x: x[1], reverse=True)

        # Da dang hoa: shuffle nhung bai hat co similarity xap xi nhau
        sim_scores = self._diversify(sim_scores)

        # Lay top N
        top_tracks = []
        for i, score in sim_scores[:top_n]:
            track = self.df.iloc[i].to_dict()
            track["similarity"] = round(float(score), 4)
            track["similarity_pct"] = round(float(score) * 100, 1)
            top_tracks.append(track)

        return top_tracks

    def _diversify(self, sim_scores: list) -> list:
        """
        Da dang hoa ket qua: nhung bai hat co similarity xap xi nhau
        (chenh lech < SIMILARITY_JITTER_THRESHOLD) se duoc shuffle ngau nhien
        de tranh hien tuong 'bong bong loc' (filter bubble).
        """
        if len(sim_scores) <= 1:
            return sim_scores

        result = []
        group = [sim_scores[0]]

        for j in range(1, len(sim_scores)):
            if abs(sim_scores[j][1] - group[0][1]) < SIMILARITY_JITTER_THRESHOLD:
                group.append(sim_scores[j])
            else:
                random.shuffle(group)
                result.extend(group)
                group = [sim_scores[j]]

        random.shuffle(group)
        result.extend(group)
        return result

    def get_track_features(self, track_id: int) -> dict | None:
        """Tra ve chi tiet features cua 1 bai hat"""
        track = self.get_track_by_id(track_id)
        if track is None:
            return None
        
        features = {f: track[f] for f in AUDIO_FEATURES}
        return {
            "track": track,
            "features": features,
            "feature_names": AUDIO_FEATURES
        }

    def get_stats(self) -> dict:
        """Thong ke tong quat ve dataset"""
        return {
            "total_tracks": len(self.df),
            "total_artists": self.df["artist_name"].nunique(),
            "total_genres": self.df["genre"].nunique(),
            "genres": self.get_genres(),
            "year_range": {
                "min": int(self.df["year"].min()),
                "max": int(self.df["year"].max())
            },
            "avg_features": {
                f: round(float(self.df[f].mean()), 3)
                for f in AUDIO_FEATURES
            }
        }
