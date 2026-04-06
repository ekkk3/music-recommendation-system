"""
Music Recommendation Engine
Phuong phap: Content-based Filtering + Cosine Similarity
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

# ============================================================
# Cac dac trung am nhac su dung de tinh toan do tuong dong
# ============================================================
AUDIO_FEATURES = [
    "danceability", "energy", "valence", "tempo",
    "acousticness", "instrumentalness", "liveness", "speechiness"
]

# ============================================================
# Dinh nghia cac tam trang (mood) va dieu kien loc
# ============================================================
MOOD_FILTERS = {
    "happy": {
        "label": "Vui ve / Nang luong",
        "conditions": {"valence": (0.6, 1.0), "energy": (0.6, 1.0)}
    },
    "sad": {
        "label": "Buon / Tram lang",
        "conditions": {"valence": (0.0, 0.35), "energy": (0.0, 0.5)}
    },
    "relax": {
        "label": "Thu gian / Binh yen",
        "conditions": {"energy": (0.0, 0.45), "acousticness": (0.3, 1.0)}
    },
    "party": {
        "label": "Soi dong / Party",
        "conditions": {"danceability": (0.65, 1.0), "energy": (0.6, 1.0)}
    },
    "focus": {
        "label": "Tap trung / Lam viec",
        "conditions": {"instrumentalness": (0.1, 1.0), "energy": (0.2, 0.6)}
    },
}


class RecommendationEngine:
    """
    Content-based Music Recommendation Engine
    
    Pipeline:
    1. Load dataset tu CSV
    2. Chuan hoa features bang MinMaxScaler
    3. Tinh ma tran Cosine Similarity (NxN)
    4. Khi nguoi dung chon bai hat -> tra ve top-N bai hat tuong tu nhat
    """

    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), "data", "tracks.csv")
        
        self.data_path = data_path
        self.df = None
        self.scaler = MinMaxScaler()
        self.feature_matrix = None
        self.similarity_matrix = None
        self._load_and_process()

    def _load_and_process(self):
        """Buoc 1-3: Load, chuan hoa, tinh similarity matrix"""
        # Buoc 1: Load dataset
        self.df = pd.read_csv(self.data_path)
        self.df = self.df.dropna(subset=AUDIO_FEATURES)
        self.df = self.df.drop_duplicates(subset=["track_name", "artist_name"])
        self.df = self.df.reset_index(drop=True)

        # Buoc 2: Chuan hoa features ve [0, 1]
        self.feature_matrix = self.scaler.fit_transform(self.df[AUDIO_FEATURES])

        # Buoc 3: Tinh ma tran Cosine Similarity
        self.similarity_matrix = cosine_similarity(self.feature_matrix)

        print(f"[Engine] Loaded {len(self.df)} tracks, similarity matrix: {self.similarity_matrix.shape}")

    def get_all_tracks(self) -> list:
        """Tra ve danh sach tat ca bai hat"""
        return self.df.to_dict(orient="records")

    def get_genres(self) -> list:
        """Tra ve danh sach cac the loai nhac"""
        return sorted(self.df["genre"].unique().tolist())

    def get_moods(self) -> list:
        """Tra ve danh sach cac mood"""
        return [{"key": k, "label": v["label"]} for k, v in MOOD_FILTERS.items()]

    def get_track_by_id(self, track_id: int) -> dict | None:
        """Tim bai hat theo ID"""
        row = self.df[self.df["id"] == track_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def search_tracks(self, query: str, limit: int = 20) -> list:
        """Tim kiem bai hat theo ten hoac nghe si"""
        q = query.lower().strip()
        if not q:
            return self.df.head(limit).to_dict(orient="records")
        
        mask = (
            self.df["track_name"].str.lower().str.contains(q, na=False) |
            self.df["artist_name"].str.lower().str.contains(q, na=False)
        )
        return self.df[mask].head(limit).to_dict(orient="records")

    def recommend(
        self,
        track_id: int,
        genre: str = None,
        mood: str = None,
        top_n: int = 10
    ) -> list:
        """
        Buoc 4: Goi y nhac
        
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

        # Lay similarity scores cua bai hat nay voi tat ca bai hat khac
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Loc bo chinh bai hat do
        sim_scores = [(i, s) for i, s in sim_scores if i != idx]

        # Loc theo genre
        if genre and genre.lower() not in ("all", "tat ca", ""):
            valid_indices = set(self.df.index[self.df["genre"] == genre])
            sim_scores = [(i, s) for i, s in sim_scores if i in valid_indices]

        # Loc theo mood
        if mood and mood.lower() not in ("all", "tat ca", ""):
            mood_config = MOOD_FILTERS.get(mood)
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

        # Lay top N
        top_tracks = []
        for i, score in sim_scores[:top_n]:
            track = self.df.iloc[i].to_dict()
            track["similarity"] = round(float(score), 4)
            track["similarity_pct"] = round(float(score) * 100, 1)
            top_tracks.append(track)

        return top_tracks

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
